import { GroupManager } from './groupManager.js';
import { SelectionManager } from './selectionManager.js';

export class ServerManager {
    constructor() {
        this.servers = [];
        this.groupManager = new GroupManager();
        this.selectionManager = new SelectionManager();
        
        // DOM이 로드된 후 초기화
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.initializeData();
                this.initializeEventListeners();
            });
        } else {
            this.initializeData();
            this.initializeEventListeners();
        }

        // 그룹 업데이트 이벤트 리스너
        document.addEventListener('groupsUpdated', () => {
            this.updateServerList();
        });
    }

    async initializeData() {
        try {
            await this.loadServers();
            await this.groupManager.loadGroups();
            this.updateServerList();
            this.updateServerGroups();
        } catch (error) {
            console.error('데이터 로드 실패:', error);
            alert('데이터 로드에 실패했습니다: ' + error.message);
        }
    }

    initializeEventListeners() {
        const addServerBtn = document.getElementById('addServerBtn');
        const saveServerBtn = document.getElementById('saveServerBtn');

        if (addServerBtn) addServerBtn.addEventListener('click', () => this.showServerModal());
        if (saveServerBtn) saveServerBtn.addEventListener('click', () => this.saveServer());
    }

    async loadServers() {
        try {
            const response = await fetch('/api/servers');
            if (!response.ok) {
                throw new Error('서버 데이터 로드 실패');
            }
            const data = await response.json();
            this.servers = data.servers || [];
            return this.servers;
        } catch (error) {
            console.error('서버 데이터 로드 실패:', error);
            throw error;
        }
    }

    updateServerList() {
        const serverList = document.getElementById('monitorServerList');
        if (!serverList) return;

        serverList.innerHTML = '';

        this.servers.forEach(server => {
            const serverItem = document.createElement('div');
            serverItem.className = 'server-item';
            serverItem.dataset.address = server.address;
            
            serverItem.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <div class="server-info">
                        <div class="server-address">${server.address}</div>
                        ${server.description ? `<small class="text-muted">${server.description}</small>` : ''}
                    </div>
                    <div class="server-groups">
                        ${this.renderServerGroups(server)}
                    </div>
                </div>
            `;

            serverList.appendChild(serverItem);
        });
    }

    renderServerGroups(server) {
        if (!server.groups || server.groups.length === 0) return '';
        
        return server.groups
            .map(groupId => {
                const group = this.groupManager.groups.find(g => g.id === groupId);
                return group ? `<span class="badge bg-secondary">${group.name}</span>` : '';
            })
            .join('');
    }

    async saveServer() {
        const addressInput = document.getElementById('serverAddress');
        const descriptionInput = document.getElementById('serverDescription');
        const groupSelect = document.getElementById('serverGroupSelect');
        
        const address = addressInput.value.trim();
        const description = descriptionInput.value.trim();
        const selectedGroups = Array.from(groupSelect.selectedOptions).map(option => parseInt(option.value));

        if (!address) {
            alert('서버 주소를 입력하세요.');
            return;
        }

        try {
            const response = await fetch('/api/servers', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    address: address,
                    description: description,
                    groups: selectedGroups
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                await this.loadServers();
                this.updateServerList();
                
                const modal = bootstrap.Modal.getInstance(document.getElementById('serverModal'));
                modal.hide();
                addressInput.value = '';
                descriptionInput.value = '';
                groupSelect.selectedIndex = -1;
                
                alert('서버가 성공적으로 추가되었습니다.');
            } else {
                throw new Error(data.error || '서버 저장에 실패했습니다.');
            }
        } catch (error) {
            console.error('서버 저장 실패:', error);
            alert(error.message);
        }
    }

    async deleteServer(serverId) {
        if (!confirm('서버를 삭제하시겠습니까?')) return;

        try {
            const response = await fetch(`/api/servers/${serverId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                await this.loadServers();
                this.updateServerList();
            } else {
                alert('서버 삭제에 실패했습니다.');
            }
        } catch (error) {
            console.error('서버 삭제 중 오류 발생:', error);
            alert('서버 삭제 중 오류가 발생했습니다.');
        }
    }

    showServerModal(server = null) {
        const modal = document.getElementById('serverModal');
        const addressInput = document.getElementById('serverAddress');
        const descriptionInput = document.getElementById('serverDescription');
        const groupSelect = document.getElementById('serverGroupSelect');
        
        addressInput.value = '';
        descriptionInput.value = '';
        
        // 그룹 목록 업데이트
        groupSelect.innerHTML = this.groupManager.groups.map(group => 
            `<option value="${group.id}">${group.name}</option>`
        ).join('');
        groupSelect.selectedIndex = -1;

        if (server) {
            addressInput.value = server.address;
            addressInput.disabled = true;
            descriptionInput.value = server.description || '';
            
            Array.from(groupSelect.options).forEach(option => {
                option.selected = server.groups.includes(parseInt(option.value));
            });
        } else {
            addressInput.disabled = false;
        }

        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
    }

    updateServerGroups() {
        const groupsContainer = document.getElementById('serverGroups');
        if (!groupsContainer) return;

        groupsContainer.innerHTML = '';

        this.groupManager.groups.forEach(group => {
            const groupItem = document.createElement('div');
            groupItem.className = 'group-item';
            groupItem.dataset.groupId = group.id;
            
            groupItem.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <div class="group-info">
                        <div class="group-name">${group.name}</div>
                        ${group.description ? `<small class="text-muted">${group.description}</small>` : ''}
                    </div>
                    <div class="server-count">
                        <span class="badge bg-light text-dark">${group.servers.length}개 서버</span>
                    </div>
                </div>
            `;

            groupsContainer.appendChild(groupItem);
        });
    }

    getServerById(serverId) {
        return this.servers.find(s => s.id === serverId);
    }
} 