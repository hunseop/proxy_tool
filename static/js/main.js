document.addEventListener('DOMContentLoaded', function() {
    // 서버 목록 (로컬 스토리지에서 로드)
    let servers = JSON.parse(localStorage.getItem('proxyServers') || '[]');
    
    // 현재 화면 (대시보드, 세션 관리, 설정)
    let currentView = 'dashboard';
    
    // 모니터링 활성화 상태
    let isMonitoring = false;
    
    // 모달 초기화
    const addServerModal = new bootstrap.Modal(document.getElementById('addServerModal'));
    
    // CPU, 메모리 임계값
    let cpuThreshold = 80;  // 기본값
    let memoryThreshold = 75;  // 기본값
    
    // 이벤트 리스너 설정
    document.getElementById('addServerBtn').addEventListener('click', showAddServerModal);
    document.getElementById('saveServerBtn').addEventListener('click', saveServer);
    document.getElementById('startMonitoringBtn').addEventListener('click', startMonitoring);
    document.getElementById('stopMonitoringBtn').addEventListener('click', stopMonitoring);
    document.getElementById('sessionLink').addEventListener('click', () => switchView('sessionManager'));
    document.getElementById('configLink').addEventListener('click', () => switchView('configManager'));
    document.getElementById('sessionSearchBtn').addEventListener('click', loadSessionData);
    document.getElementById('sessionRefreshBtn').addEventListener('click', () => loadSessionData(true));
    document.getElementById('saveConfigBtn').addEventListener('click', saveConfig);
    
    // 초기화
    init();
    
    /**
     * 초기화 함수
     */
    function init() {
        // 서버 목록 로드
        updateServerList();
        
        // 설정 로드
        loadConfig();
        
        // 세션 서버 선택 드롭다운 업데이트
        updateSessionServerSelect();
        
        // 리소스 데이터를 주기적으로 가져오는 타이머 설정
        setInterval(fetchResourceData, 5000);
    }
    
    /**
     * 서버 추가 모달 표시
     */
    function showAddServerModal() {
        document.getElementById('serverAddress').value = '';
        addServerModal.show();
    }
    
    /**
     * 서버 추가
     */
    function saveServer() {
        const serverAddress = document.getElementById('serverAddress').value.trim();
        
        if (!serverAddress) {
            alert('서버 주소를 입력하세요.');
            return;
        }
        
        // 중복 체크
        if (servers.includes(serverAddress)) {
            alert('이미 등록된 서버입니다.');
            return;
        }
        
        // 서버 추가
        servers.push(serverAddress);
        
        // 로컬 스토리지에 저장
        localStorage.setItem('proxyServers', JSON.stringify(servers));
        
        // 서버 목록 업데이트
        updateServerList();
        
        // 세션 서버 선택 드롭다운 업데이트
        updateSessionServerSelect();
        
        // 모달 닫기
        addServerModal.hide();
    }
    
    /**
     * 서버 목록 업데이트
     */
    function updateServerList() {
        const serverList = document.getElementById('serverList');
        serverList.innerHTML = '';
        
        servers.forEach(server => {
            const item = document.createElement('a');
            item.className = 'list-group-item list-group-item-action';
            item.innerHTML = `
                ${server}
                <span class="badge bg-danger remove-server" data-server="${server}">삭제</span>
            `;
            serverList.appendChild(item);
        });
        
        // 서버 삭제 이벤트 리스너 추가
        document.querySelectorAll('.remove-server').forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const server = this.getAttribute('data-server');
                removeServer(server);
            });
        });
    }
    
    /**
     * 세션 서버 선택 드롭다운 업데이트
     */
    function updateSessionServerSelect() {
        const select = document.getElementById('sessionServerSelect');
        select.innerHTML = '';
        
        servers.forEach(server => {
            const option = document.createElement('option');
            option.value = server;
            option.textContent = server;
            select.appendChild(option);
        });
    }
    
    /**
     * 서버 삭제
     */
    function removeServer(server) {
        if (confirm(`${server} 서버를 삭제하시겠습니까?`)) {
            servers = servers.filter(s => s !== server);
            localStorage.setItem('proxyServers', JSON.stringify(servers));
            updateServerList();
            updateSessionServerSelect();
        }
    }
    
    /**
     * 모니터링 시작
     */
    function startMonitoring() {
        if (servers.length === 0) {
            alert('서버를 먼저 추가해주세요.');
            return;
        }
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const interval = document.getElementById('interval').value;
        
        fetch('/api/monitoring/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                hosts: servers,
                username: username,
                password: password,
                interval: parseInt(interval)
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                isMonitoring = true;
                alert('모니터링이 시작되었습니다.');
                
                // 버튼 상태 변경
                document.getElementById('startMonitoringBtn').disabled = true;
                document.getElementById('stopMonitoringBtn').disabled = false;
                
                // 즉시 데이터 조회
                fetchResourceData();
            } else {
                alert(`오류: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('모니터링 시작 중 오류가 발생했습니다.');
        });
    }
    
    /**
     * 모니터링 중지
     */
    function stopMonitoring() {
        fetch('/api/monitoring/stop', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                isMonitoring = false;
                alert('모니터링이 중지되었습니다.');
                
                // 버튼 상태 변경
                document.getElementById('startMonitoringBtn').disabled = false;
                document.getElementById('stopMonitoringBtn').disabled = true;
            } else {
                alert(`오류: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('모니터링 중지 중 오류가 발생했습니다.');
        });
    }
    
    /**
     * 리소스 데이터 조회
     */
    function fetchResourceData() {
        if (!isMonitoring || servers.length === 0) return;
        
        // 모든 서버의 데이터를 가져오기 위한 Promise 배열
        const promises = servers.map(server => 
            fetch('/api/resources', {
                headers: {
                    'X-Monitor-Host': server
                }
            })
            .then(response => response.json())
            .then(data => ({ [server]: data }))
            .catch(error => {
                console.error(`Error fetching data for ${server}:`, error);
                return { [server]: { error: error.message } };
            })
        );
        
        // 모든 서버의 데이터를 병합
        Promise.all(promises)
            .then(results => {
                const data = results.reduce((acc, curr) => ({ ...acc, ...curr }), {});
                updateResourceTable(data);
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }
    
    /**
     * 리소스 테이블 업데이트
     */
    function updateResourceTable(data) {
        const resourceTable = document.getElementById('resourceData');
        resourceTable.innerHTML = '';
        
        // 서버별 데이터가 없는 경우
        if (Object.keys(data).length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = `<td colspan="11" class="text-center">모니터링 데이터가 없습니다. 모니터링을 시작해주세요.</td>`;
            resourceTable.appendChild(row);
            return;
        }
        
        // 데이터 행 추가
        for (const host in data) {
            const resourceData = data[host];
            const row = document.createElement('tr');
            
            // CPU, 메모리 경고 클래스 추가
            const cpuClass = parseInt(resourceData.cpu) >= cpuThreshold ? 'warning-cpu' : '';
            const memoryClass = parseInt(resourceData.memory) >= memoryThreshold ? 'warning-memory' : '';
            
            row.innerHTML = `
                <td>${host}</td>
                <td>${resourceData.date}</td>
                <td>${resourceData.time}</td>
                <td class="${cpuClass}">${resourceData.cpu === 'error' ? 'N/A' : resourceData.cpu}</td>
                <td class="${memoryClass}">${resourceData.memory === 'error' ? 'N/A' : resourceData.memory}</td>
                <td>${resourceData.uc === 'error' ? 'N/A' : resourceData.uc}</td>
                <td>${resourceData.http === 'error' ? 'N/A' : resourceData.http}</td>
                <td>${resourceData.https === 'error' ? 'N/A' : resourceData.https}</td>
                <td>${resourceData.ftp === 'error' ? 'N/A' : resourceData.ftp}</td>
                <td>${resourceData.cc === 'error' ? 'N/A' : resourceData.cc}</td>
                <td>${resourceData.cs === 'error' ? 'N/A' : resourceData.cs}</td>
            `;
            
            resourceTable.appendChild(row);
        }
    }
    
    /**
     * 세션 데이터 로드
     */
    function loadSessionData(isRefresh = false) {
        const server = document.getElementById('sessionServerSelect').value;
        
        if (!server) {
            alert('선택된 서버가 없습니다.');
            return;
        }
        
        const search = isRefresh ? '' : document.getElementById('sessionSearch').value.trim();
        const sessionData = document.getElementById('sessionData');
        
        // 로딩 표시
        sessionData.innerHTML = '<tr><td colspan="8" class="text-center"><div class="loading"></div> 세션 데이터를 로드 중입니다...</td></tr>';
        
        let url = `/api/sessions/${server}`;
        if (search) {
            url += `?search=${encodeURIComponent(search)}`;
        }
        
        fetch(url)
        .then(response => response.json())
        .then(data => {
            updateSessionTable(data);
        })
        .catch(error => {
            console.error('Error:', error);
            sessionData.innerHTML = `<tr><td colspan="8" class="text-center text-danger">세션 데이터 로드 실패: ${error.message}</td></tr>`;
        });
    }
    
    /**
     * 세션 테이블 업데이트
     */
    function updateSessionTable(data) {
        const sessionData = document.getElementById('sessionData');
        sessionData.innerHTML = '';
        
        if (data.length === 0) {
            sessionData.innerHTML = '<tr><td colspan="8" class="text-center">세션 데이터가 없습니다.</td></tr>';
            return;
        }
        
        data.forEach(session => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${session['Creation Time']}</td>
                <td>${session['Username']}</td>
                <td>${session['Client IP']}</td>
                <td>${session['Proxy IP']}</td>
                <td>${session['URL']}</td>
                <td>${session['CL Bytes Received']}</td>
                <td>${session['CL Bytes Sent']}</td>
                <td>${session['Age(seconds)']}</td>
            `;
            sessionData.appendChild(row);
        });
    }
    
    /**
     * 화면 전환
     */
    function switchView(view) {
        // 현재 활성화된 메뉴 아이템의 활성화 해제
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // 새 메뉴 아이템 활성화
        if (view === 'dashboard') {
            document.querySelector('.nav-item:nth-child(1) .nav-link').classList.add('active');
        } else if (view === 'sessionManager') {
            document.querySelector('.nav-item:nth-child(2) .nav-link').classList.add('active');
        } else if (view === 'configManager') {
            document.querySelector('.nav-item:nth-child(3) .nav-link').classList.add('active');
        }
        
        // 현재 화면 숨기기
        document.getElementById(currentView).classList.add('d-none');
        
        // 새 화면 표시
        document.getElementById(view).classList.remove('d-none');
        
        // 현재 화면 업데이트
        currentView = view;
        
        // 세션 관리 화면으로 전환한 경우, 서버가 있으면 데이터 로드
        if (view === 'sessionManager' && servers.length > 0) {
            loadSessionData(true);
        }
    }
    
    /**
     * 설정 로드
     */
    function loadConfig() {
        fetch('/api/config')
        .then(response => response.json())
        .then(data => {
            document.getElementById('sshUsername').value = data.ssh_username || '';
            document.getElementById('sshPassword').value = data.ssh_password || '';
            document.getElementById('snmpCommunity').value = data.snmp_community || '';
            document.getElementById('cpuThreshold').value = data.cpu_threshold || '';
            document.getElementById('memoryThreshold').value = data.memory_threshold || '';
            
            // 임계값 업데이트
            cpuThreshold = data.cpu_threshold || cpuThreshold;
            memoryThreshold = data.memory_threshold || memoryThreshold;
            
            // 모니터링 폼에도 값 설정
            document.getElementById('username').value = data.ssh_username || '';
            document.getElementById('password').value = data.ssh_password || '';
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
    
    /**
     * 설정 저장
     */
    function saveConfig() {
        const config = {
            ssh_username: document.getElementById('sshUsername').value,
            ssh_password: document.getElementById('sshPassword').value,
            snmp_community: document.getElementById('snmpCommunity').value,
            cpu_threshold: parseInt(document.getElementById('cpuThreshold').value),
            memory_threshold: parseInt(document.getElementById('memoryThreshold').value)
        };
        
        fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('설정이 저장되었습니다.');
                
                // 임계값 업데이트
                cpuThreshold = config.cpu_threshold;
                memoryThreshold = config.memory_threshold;
                
                // 모니터링 폼에도 값 설정
                document.getElementById('username').value = config.ssh_username;
                document.getElementById('password').value = config.ssh_password;
            } else {
                alert(`오류: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('설정 저장 중 오류가 발생했습니다.');
        });
    }
}); 