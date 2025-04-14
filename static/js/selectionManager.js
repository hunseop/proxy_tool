export class SelectionManager {
    constructor() {
        this.selectedServers = new Set();
        this.selectedSessionServers = new Set();
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // 서버 선택 관련 이벤트
        const selectAllBtn = document.getElementById('selectAllServers');
        const clearSelectionBtn = document.getElementById('clearServerSelection');
        const serverSearchInput = document.getElementById('serverSearch');
        const applySelectionBtn = document.getElementById('applyServerSelection');

        if (selectAllBtn) selectAllBtn.addEventListener('click', () => this.selectAllServers());
        if (clearSelectionBtn) clearSelectionBtn.addEventListener('click', () => this.clearSelection());
        if (serverSearchInput) serverSearchInput.addEventListener('input', (e) => this.filterServerList(e.target.value));
        if (applySelectionBtn) applySelectionBtn.addEventListener('click', () => this.applySelection());

        // 서버 목록 클릭 이벤트 위임
        const monitorServerList = document.getElementById('monitorServerList');
        if (monitorServerList) {
            monitorServerList.addEventListener('click', (e) => {
                const serverItem = e.target.closest('.server-item');
                if (serverItem) {
                    const serverAddress = serverItem.dataset.address;
                    this.toggleServerSelection(serverAddress);
                }
            });
        }

        // 그룹 목록 클릭 이벤트 위임
        const serverGroups = document.getElementById('serverGroups');
        if (serverGroups) {
            serverGroups.addEventListener('click', (e) => {
                const groupItem = e.target.closest('.group-item');
                if (groupItem) {
                    const groupId = parseInt(groupItem.dataset.groupId);
                    this.toggleGroupSelection(groupId);
                }
            });
        }

        // 세션 서버 선택 관련 이벤트도 동일하게 처리
        const sessionServerList = document.getElementById('sessionServerList');
        if (sessionServerList) {
            sessionServerList.addEventListener('click', (e) => {
                const serverItem = e.target.closest('.server-item');
                if (serverItem) {
                    const serverAddress = serverItem.dataset.address;
                    this.toggleSessionServerSelection(serverAddress);
                }
            });
        }

        // 세션 서버 선택 관련 이벤트
        const selectAllSessionBtn = document.getElementById('selectAllSessionServers');
        const clearSessionSelectionBtn = document.getElementById('clearSessionServerSelection');
        const sessionServerSearchInput = document.getElementById('sessionServerSearch');
        const applySessionSelectionBtn = document.getElementById('applySessionServerSelection');

        if (selectAllSessionBtn) selectAllSessionBtn.addEventListener('click', () => this.selectAllSessionServers());
        if (clearSessionSelectionBtn) clearSessionSelectionBtn.addEventListener('click', () => this.clearSessionSelection());
        if (sessionServerSearchInput) sessionServerSearchInput.addEventListener('input', (e) => this.filterSessionServerList(e.target.value));
        if (applySessionSelectionBtn) applySessionSelectionBtn.addEventListener('click', () => this.applySessionSelection());
    }

    selectAllServers() {
        this.servers.forEach(server => {
            this.selectedServers.add(server.address);
        });
        this.updateServerList();
        this.updateGroupCheckboxes();
    }

    clearSelection() {
        this.selectedServers.clear();
        this.updateServerList();
        this.updateGroupCheckboxes();
    }

    filterServerList(searchTerm) {
        const serverItems = document.querySelectorAll('.server-item');
        serverItems.forEach(item => {
            const serverName = item.querySelector('.server-address').textContent;
            if (serverName.toLowerCase().includes(searchTerm.toLowerCase())) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }

    applySelection() {
        const dropdownButton = document.getElementById('serverSelectDropdown');
        const selectedCount = this.selectedServers.size;
        
        if (selectedCount === 0) {
            dropdownButton.textContent = '서버 선택';
        } else {
            dropdownButton.textContent = `선택된 서버 ${selectedCount}개`;
        }
        
        document.dispatchEvent(new CustomEvent('serverSelectionChanged', {
            detail: {
                servers: [...this.selectedServers]
            }
        }));
    }

    selectAllSessionServers() {
        this.servers.forEach(server => {
            this.selectedSessionServers.add(server.address);
        });
        this.updateSessionServerList();
        this.updateSessionGroupCheckboxes();
    }

    clearSessionSelection() {
        this.selectedSessionServers.clear();
        this.updateSessionServerList();
        this.updateSessionGroupCheckboxes();
    }

    filterSessionServerList(searchTerm) {
        const serverItems = document.querySelectorAll('#sessionServerList .form-check');
        serverItems.forEach(item => {
            const serverName = item.querySelector('label').textContent;
            if (serverName.toLowerCase().includes(searchTerm.toLowerCase())) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }

    applySessionSelection() {
        const dropdownButton = document.getElementById('sessionServerSelectDropdown');
        const selectedCount = this.selectedSessionServers.size;
        
        if (selectedCount === 0) {
            dropdownButton.textContent = '서버 선택';
        } else {
            dropdownButton.textContent = `선택된 서버 ${selectedCount}개`;
        }
        
        document.dispatchEvent(new CustomEvent('sessionServerSelectionChanged', {
            detail: {
                servers: [...this.selectedSessionServers]
            }
        }));
    }

    updateGroupCheckboxes() {
        document.querySelectorAll('.group-checkbox').forEach(checkbox => {
            const groupId = parseInt(checkbox.value);
            const group = this.groups.find(g => g.id === groupId);
            if (group) {
                checkbox.checked = group.servers.every(server => this.selectedServers.has(server));
            }
        });
    }

    updateSessionGroupCheckboxes() {
        document.querySelectorAll('#sessionServerGroups .group-checkbox').forEach(checkbox => {
            const groupId = parseInt(checkbox.value);
            const group = this.groups.find(g => g.id === groupId);
            if (group) {
                checkbox.checked = group.servers.every(server => this.selectedSessionServers.has(server));
            }
        });
    }

    getSelectedServers() {
        return [...this.selectedServers];
    }

    getSelectedSessionServers() {
        return [...this.selectedSessionServers];
    }

    toggleServerSelection(serverAddress) {
        if (this.selectedServers.has(serverAddress)) {
            this.selectedServers.delete(serverAddress);
        } else {
            this.selectedServers.add(serverAddress);
        }
        this.updateServerList();
    }

    toggleSessionServerSelection(serverAddress) {
        if (this.selectedSessionServers.has(serverAddress)) {
            this.selectedSessionServers.delete(serverAddress);
        } else {
            this.selectedSessionServers.add(serverAddress);
        }
        this.updateSessionServerList();
    }

    toggleGroupSelection(groupId) {
        const group = this.groups.find(g => g.id === groupId);
        if (!group) return;

        const allSelected = group.servers.every(server => this.selectedServers.has(server));
        
        if (allSelected) {
            // 그룹의 모든 서버가 선택되어 있으면 선택 해제
            group.servers.forEach(server => this.selectedServers.delete(server));
        } else {
            // 그룹의 모든 서버를 선택
            group.servers.forEach(server => this.selectedServers.add(server));
        }
        
        this.updateServerList();
        this.updateGroupCheckboxes();
    }

    updateServerList() {
        const serverList = document.getElementById('monitorServerList');
        if (!serverList) return;

        const serverItems = serverList.querySelectorAll('.server-item');
        serverItems.forEach(item => {
            const serverAddress = item.dataset.address;
            if (this.selectedServers.has(serverAddress)) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
    }

    updateSessionServerList() {
        const serverList = document.getElementById('sessionServerList');
        if (!serverList) return;

        const serverItems = serverList.querySelectorAll('.server-item');
        serverItems.forEach(item => {
            const serverAddress = item.dataset.address;
            if (this.selectedSessionServers.has(serverAddress)) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
    }
} 