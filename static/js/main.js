import { ServerManager } from './serverManager.js';
import { MonitoringManager } from './monitoringManager.js';
import { SessionManager } from './sessionManager.js';
import { ConfigManager } from './configManager.js';
import { UIManager } from './uiManager.js';

// 각 매니저 인스턴스 생성
const serverManager = new ServerManager();
const monitoringManager = new MonitoringManager();
const sessionManager = new SessionManager();
const configManager = new ConfigManager();
const uiManager = new UIManager();

// 서버 선택 변경 이벤트 리스너
document.addEventListener('serverSelectionChanged', (e) => {
    const selectedServers = e.detail.servers;
    monitoringManager.setSelectedServers(selectedServers);
});

// 세션 서버 선택 변경 이벤트 리스너
document.addEventListener('sessionServerSelectionChanged', (e) => {
    const selectedServers = e.detail.servers;
    sessionManager.setSelectedServers(selectedServers);
});

// 그룹 업데이트 이벤트 리스너
document.addEventListener('groupsUpdated', () => {
    serverManager.updateServerList();
    serverManager.updateServerGroups();
});

// 모니터링 시작/중지 버튼 이벤트 리스너
const startMonitoringBtn = document.getElementById('startMonitoringBtn');
const stopMonitoringBtn = document.getElementById('stopMonitoringBtn');

if (startMonitoringBtn) {
    startMonitoringBtn.addEventListener('click', () => {
        const interval = document.getElementById('interval').value;
        monitoringManager.startMonitoring(interval);
        startMonitoringBtn.disabled = true;
        stopMonitoringBtn.disabled = false;
    });
}

if (stopMonitoringBtn) {
    stopMonitoringBtn.addEventListener('click', () => {
        monitoringManager.stopMonitoring();
        startMonitoringBtn.disabled = false;
        stopMonitoringBtn.disabled = true;
    });
}

// 세션 새로고침 버튼 이벤트 리스너
const sessionRefreshBtn = document.getElementById('sessionRefreshBtn');
if (sessionRefreshBtn) {
    sessionRefreshBtn.addEventListener('click', () => {
        sessionManager.refreshSessions();
    });
}

// 설정 저장 버튼 이벤트 리스너
const saveConfigBtn = document.getElementById('saveConfigBtn');
if (saveConfigBtn) {
    saveConfigBtn.addEventListener('click', () => {
        configManager.saveConfig();
    });
}

// 세션 검색 이벤트 리스너
const sessionSearchBtn = document.getElementById('sessionSearchBtn');
if (sessionSearchBtn) {
    sessionSearchBtn.addEventListener('click', () => {
        const searchTerm = document.getElementById('sessionSearch').value;
        sessionManager.searchSessions(searchTerm);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // 탭 전환 이벤트 리스너
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const view = this.getAttribute('data-view');
            if (view) {
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                this.classList.add('active');
                document.querySelectorAll('.tab-pane').forEach(pane => {
                    if (pane.id === view) {
                        pane.classList.add('show', 'active');
                    } else {
                        pane.classList.remove('show', 'active');
                    }
                });
            }
        });
    });
    
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
        }
    }
}); 