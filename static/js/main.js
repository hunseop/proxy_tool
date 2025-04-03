document.addEventListener('DOMContentLoaded', function() {
    // 서버 데이터 (로컬 스토리지에서 로드)
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
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            switchView(this.getAttribute('data-view'));
        });
    });
    
    document.getElementById('addServerBtn').addEventListener('click', () => addServerModal.show());
    document.getElementById('saveServerBtn').addEventListener('click', saveServer);
    document.getElementById('startMonitoringBtn').addEventListener('click', startMonitoring);
    document.getElementById('stopMonitoringBtn').addEventListener('click', stopMonitoring);
    document.getElementById('sessionSearchBtn').addEventListener('click', loadSessionData);
    document.getElementById('sessionRefreshBtn').addEventListener('click', () => loadSessionData(true));
    document.getElementById('saveConfigBtn').addEventListener('click', saveConfig);
    
    // 초기화
    init();
    
    /**
     * 초기화 함수
     */
    function init() {
        // 서버 목록 업데이트
        updateServerList();
        
        // 설정 로드
        loadConfig();
        
        // 세션 서버 선택 드롭다운 업데이트
        updateSessionServerSelect();
        
        // 리소스 데이터를 주기적으로 가져오는 타이머 설정
        setInterval(fetchResourceData, 5000);
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
        
        // 서버 중복 체크
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
        const container = document.getElementById('serverGroups');
        const monitorSelect = document.getElementById('monitorServerSelect');
        
        // 설정 페이지의 서버 목록 업데이트
        container.innerHTML = '';
        servers.forEach(server => {
            const serverItem = document.createElement('div');
            serverItem.className = 'server-item';
            serverItem.innerHTML = `
                <span>${server}</span>
                <button class="btn btn-sm btn-outline-danger" onclick="removeServer('${server}')">삭제</button>
            `;
            container.appendChild(serverItem);
        });
        
        // 모니터링 서버 선택 드롭다운 업데이트
        monitorSelect.innerHTML = '<option value="">서버 선택</option>';
        servers.forEach(server => {
            const option = document.createElement('option');
            option.value = server;
            option.textContent = server;
            monitorSelect.appendChild(option);
        });
        
        // 전역 함수로 삭제 기능 추가
        window.removeServer = function(server) {
            if (confirm(`"${server}" 서버를 삭제하시겠습니까?`)) {
                servers = servers.filter(s => s !== server);
                localStorage.setItem('proxyServers', JSON.stringify(servers));
                updateServerList();
                updateSessionServerSelect();
            }
        };
    }
    
    /**
     * 세션 서버 선택 드롭다운 업데이트
     */
    function updateSessionServerSelect() {
        const select = document.getElementById('sessionServerSelect');
        select.innerHTML = '<option value="">서버 선택</option>';
        
        servers.forEach(server => {
            const option = document.createElement('option');
            option.value = server;
            option.textContent = server;
            select.appendChild(option);
        });
    }
    
    /**
     * 모니터링 시작
     */
    function startMonitoring() {
        const selectedServer = document.getElementById('monitorServerSelect').value;
        
        if (!selectedServer) {
            alert('서버를 선택해주세요.');
            return;
        }
        
        const interval = document.getElementById('interval').value;
        
        fetch('/api/monitoring/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                hosts: [selectedServer],
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
                document.getElementById('monitorServerSelect').disabled = true;
                
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
                document.getElementById('monitorServerSelect').disabled = false;
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
        const selectedServer = document.getElementById('monitorServerSelect').value;
        if (!isMonitoring) return;
        
        fetch('/api/resources', {
            headers: {
                'X-Monitor-Host': selectedServer
            }
        })
        .then(response => response.json())
        .then(data => {
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
        
        if (!data || Object.keys(data).length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = `<td colspan="11" class="text-center">모니터링 데이터가 없습니다. 모니터링을 시작해주세요.</td>`;
            resourceTable.appendChild(row);
            return;
        }
        
        const row = document.createElement('tr');
        
        // CPU, 메모리 경고 클래스 추가
        const cpuClass = parseInt(data.cpu) >= cpuThreshold ? 'warning-cpu' : '';
        const memoryClass = parseInt(data.memory) >= memoryThreshold ? 'warning-memory' : '';
        
        row.innerHTML = `
            <td>${document.getElementById('monitorServerSelect').value}</td>
            <td>${data.date || 'N/A'}</td>
            <td>${data.time || 'N/A'}</td>
            <td class="${cpuClass}">${data.cpu === 'error' ? 'N/A' : data.cpu}</td>
            <td class="${memoryClass}">${data.memory === 'error' ? 'N/A' : data.memory}</td>
            <td>${data.uc === 'error' ? 'N/A' : data.uc}</td>
            <td>${data.http === 'error' ? 'N/A' : data.http}</td>
            <td>${data.https === 'error' ? 'N/A' : data.https}</td>
            <td>${data.ftp === 'error' ? 'N/A' : data.ftp}</td>
            <td>${data.cc === 'error' ? 'N/A' : data.cc}</td>
            <td>${data.cs === 'error' ? 'N/A' : data.cs}</td>
        `;
        
        resourceTable.appendChild(row);
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
        
        if (!data || data.length === 0) {
            sessionData.innerHTML = '<tr><td colspan="8" class="text-center">세션 데이터가 없습니다.</td></tr>';
            return;
        }
        
        data.forEach(session => {
            const row = document.createElement('tr');
            
            // 데이터가 undefined인 경우 'N/A' 표시
            const creationTime = session['Creation Time'] || 'N/A';
            const username = session['User Name'] || 'N/A';
            const clientIP = session['Client IP'] || 'N/A';
            const proxyIP = session['Proxy IP'] || 'N/A';
            const url = session['URL'] || 'N/A';
            const bytesReceived = session['CL Bytes Received'] || 'N/A';
            const bytesSent = session['CL Bytes Sent'] || 'N/A';
            const age = session['Age(seconds)'] || 'N/A';
            
            row.innerHTML = `
                <td data-full-text="${creationTime}">${creationTime}</td>
                <td data-full-text="${username}">${username}</td>
                <td data-full-text="${clientIP}">${clientIP}</td>
                <td data-full-text="${proxyIP}">${proxyIP}</td>
                <td data-full-text="${url}">${url}</td>
                <td data-full-text="${bytesReceived}">${bytesReceived}</td>
                <td data-full-text="${bytesSent}">${bytesSent}</td>
                <td data-full-text="${age}">${age}</td>
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
        document.querySelector(`[data-view="${view}"]`).classList.add('active');
        
        // 현재 화면 숨기기
        document.getElementById(currentView).classList.add('d-none');
        
        // 새 화면 표시
        document.getElementById(view).classList.remove('d-none');
        
        // 현재 화면 업데이트
        currentView = view;
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