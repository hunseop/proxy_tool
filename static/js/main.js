import { ServerManager } from './serverManager.js';
import { MonitoringManager } from './monitoringManager.js';
import { SessionManager } from './sessionManager.js';
import { ConfigManager } from './configManager.js';
import { UIManager } from './uiManager.js';

document.addEventListener('DOMContentLoaded', function() {
    // 매니저 인스턴스 생성
    const serverManager = new ServerManager();
    const monitoringManager = new MonitoringManager();
    const sessionManager = new SessionManager();
    const configManager = new ConfigManager();
    const uiManager = new UIManager();
    
    // 모달 초기화
    const addServerModal = new bootstrap.Modal(document.getElementById('addServerModal'));
    
    // 이벤트 리스너 설정
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            uiManager.switchView(this.getAttribute('data-view'));
        });
    });
    
    document.getElementById('addServerBtn').addEventListener('click', () => addServerModal.show());
    document.getElementById('saveServerBtn').addEventListener('click', () => {
        const serverAddress = document.getElementById('serverAddress').value.trim();
        if (serverManager.saveServer(serverAddress)) {
            updateUI();
            addServerModal.hide();
        }
    });
    
    document.getElementById('startMonitoringBtn').addEventListener('click', async () => {
        const selectedServer = document.getElementById('monitorServerSelect').value;
        const interval = document.getElementById('interval').value;
        if (await monitoringManager.startMonitoring(selectedServer, interval)) {
            document.getElementById('startMonitoringBtn').disabled = true;
            document.getElementById('stopMonitoringBtn').disabled = false;
            document.getElementById('monitorServerSelect').disabled = true;
            fetchResourceData();
        }
    });
    
    document.getElementById('stopMonitoringBtn').addEventListener('click', async () => {
        if (await monitoringManager.stopMonitoring()) {
            document.getElementById('startMonitoringBtn').disabled = false;
            document.getElementById('stopMonitoringBtn').disabled = true;
            document.getElementById('monitorServerSelect').disabled = false;
        }
    });
    
    document.getElementById('sessionSearchBtn').addEventListener('click', () => loadSessionData());
    document.getElementById('sessionRefreshBtn').addEventListener('click', () => loadSessionData(true));
    document.getElementById('saveConfigBtn').addEventListener('click', saveConfig);
    
    // 초기화
    init();
    
    /**
     * 초기화 함수
     */
    async function init() {
        updateUI();
        await loadConfig();
        setInterval(fetchResourceData, 5000);
    }
    
    /**
     * UI 업데이트
     */
    function updateUI() {
        const servers = serverManager.getServers();
        uiManager.updateServerList(
            servers,
            document.getElementById('serverGroups'),
            document.getElementById('monitorServerSelect')
        );
        uiManager.updateSessionServerSelect(
            servers,
            document.getElementById('sessionServerSelect')
        );
        
        // 전역 함수로 삭제 기능 추가
        window.removeServer = function(server) {
            if (confirm(`"${server}" 서버를 삭제하시겠습니까?`)) {
                serverManager.removeServer(server);
                updateUI();
            }
        };
    }
    
    /**
     * 리소스 데이터 조회
     */
    async function fetchResourceData() {
        const selectedServer = document.getElementById('monitorServerSelect').value;
        const data = await monitoringManager.fetchResourceData(selectedServer);
        if (data) {
            const thresholds = monitoringManager.getThresholds();
            uiManager.updateResourceTable(
                data,
                document.getElementById('resourceData'),
                thresholds.cpu,
                thresholds.memory,
                selectedServer
            );
        }
    }
    
    /**
     * 세션 데이터 로드
     */
    async function loadSessionData(isRefresh = false) {
        const server = document.getElementById('sessionServerSelect').value;
        const search = isRefresh ? '' : document.getElementById('sessionSearch').value.trim();
        const sessionData = document.getElementById('sessionData');
        
        sessionData.innerHTML = '<tr><td colspan="8" class="text-center"><div class="loading"></div> 세션 데이터를 로드 중입니다...</td></tr>';
        
        const data = await sessionManager.loadSessionData(server, search, isRefresh);
        if (data) {
            uiManager.updateSessionTable(data, sessionData);
        } else {
            sessionData.innerHTML = '<tr><td colspan="8" class="text-center text-danger">세션 데이터 로드 실패</td></tr>';
        }
    }
    
    /**
     * 설정 로드
     */
    async function loadConfig() {
        const config = await configManager.loadConfig();
        if (config) {
            document.getElementById('sshUsername').value = config.ssh_username || '';
            document.getElementById('sshPassword').value = config.ssh_password || '';
            document.getElementById('snmpCommunity').value = config.snmp_community || '';
            document.getElementById('cpuThreshold').value = config.cpu_threshold || '';
            document.getElementById('memoryThreshold').value = config.memory_threshold || '';
            
            monitoringManager.setThresholds(
                config.cpu_threshold || monitoringManager.getThresholds().cpu,
                config.memory_threshold || monitoringManager.getThresholds().memory
            );
            
            document.getElementById('username').value = config.ssh_username || '';
            document.getElementById('password').value = config.ssh_password || '';
        }
    }
    
    /**
     * 설정 저장
     */
    async function saveConfig() {
        const config = {
            ssh_username: document.getElementById('sshUsername').value,
            ssh_password: document.getElementById('sshPassword').value,
            snmp_community: document.getElementById('snmpCommunity').value,
            cpu_threshold: parseInt(document.getElementById('cpuThreshold').value),
            memory_threshold: parseInt(document.getElementById('memoryThreshold').value)
        };
        
        if (await configManager.saveConfig(config)) {
            monitoringManager.setThresholds(config.cpu_threshold, config.memory_threshold);
            document.getElementById('username').value = config.ssh_username;
            document.getElementById('password').value = config.ssh_password;
        }
    }
}); 