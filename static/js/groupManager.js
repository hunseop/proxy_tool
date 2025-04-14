export class GroupManager {
    constructor() {
        this.groups = [];
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const addGroupBtn = document.getElementById('addGroupBtn');
        const saveGroupBtn = document.getElementById('saveGroupBtn');

        if (addGroupBtn) addGroupBtn.addEventListener('click', () => this.showGroupModal());
        if (saveGroupBtn) saveGroupBtn.addEventListener('click', () => this.saveGroup());
    }

    async loadGroups() {
        try {
            const response = await fetch('/api/server-groups');
            if (!response.ok) {
                throw new Error('그룹 데이터 로드 실패');
            }
            const data = await response.json();
            this.groups = data.groups || [];
            this.updateGroupsList();
            return this.groups;
        } catch (error) {
            console.error('그룹 데이터 로드 실패:', error);
            throw error;
        }
    }

    updateGroupsList() {
        const groupsList = document.getElementById('serverGroupsList');
        if (!groupsList) return;

        groupsList.innerHTML = '';

        this.groups.forEach(group => {
            const groupItem = document.createElement('div');
            groupItem.className = 'server-group-item';
            groupItem.innerHTML = `
                <div class="group-info">
                    <div class="group-info-text">
                        <div class="group-name">${group.name}</div>
                        ${group.description ? `<div class="group-description">${group.description}</div>` : ''}
                        ${this.renderGroupServers(group)}
                    </div>
                    <div class="group-actions">
                        <button class="btn action-btn edit-btn" data-group-id="${group.id}">수정</button>
                        <button class="btn action-btn delete-btn" data-group-id="${group.id}">삭제</button>
                    </div>
                </div>
            `;

            const editBtn = groupItem.querySelector('.edit-btn');
            editBtn.addEventListener('click', () => this.showGroupModal(group));

            const deleteBtn = groupItem.querySelector('.delete-btn');
            deleteBtn.addEventListener('click', () => this.deleteGroup(group.id));

            groupsList.appendChild(groupItem);
        });
    }

    renderGroupServers(group) {
        if (!group.servers || group.servers.length === 0) return '';
        
        const serverBadges = group.servers
            .map(serverId => {
                const server = this.getServerById(serverId);
                return server ? `<span class="badge badge-server">${server.address}</span>` : '';
            })
            .join('');
        
        return `<div class="group-servers">${serverBadges}</div>`;
    }

    async saveGroup() {
        const nameInput = document.getElementById('groupName');
        const descriptionInput = document.getElementById('groupDescription');
        const serverSelect = document.getElementById('groupServerSelect');
        
        const name = nameInput.value.trim();
        const description = descriptionInput.value.trim();
        const selectedServers = Array.from(serverSelect.selectedOptions).map(option => parseInt(option.value));

        if (!name) {
            alert('그룹 이름을 입력하세요.');
            return;
        }

        try {
            const response = await fetch('/api/server-groups', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: name,
                    description: description,
                    servers: selectedServers
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                await this.loadGroups();
                
                const modal = bootstrap.Modal.getInstance(document.getElementById('groupModal'));
                modal.hide();
                nameInput.value = '';
                descriptionInput.value = '';
                serverSelect.selectedIndex = -1;
                
                // 이벤트 발생
                document.dispatchEvent(new CustomEvent('groupsUpdated'));
            } else {
                throw new Error(data.error || '그룹 저장에 실패했습니다.');
            }
        } catch (error) {
            console.error('그룹 저장 실패:', error);
            alert(error.message);
        }
    }

    async deleteGroup(groupId) {
        if (!confirm('그룹을 삭제하시겠습니까?')) return;

        try {
            const response = await fetch(`/api/server-groups/${groupId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                await this.loadGroups();
                // 이벤트 발생
                document.dispatchEvent(new CustomEvent('groupsUpdated'));
            } else {
                alert('그룹 삭제에 실패했습니다.');
            }
        } catch (error) {
            console.error('그룹 삭제 중 오류 발생:', error);
            alert('그룹 삭제 중 오류가 발생했습니다.');
        }
    }

    showGroupModal(group = null) {
        const modal = document.getElementById('groupModal');
        const nameInput = document.getElementById('groupName');
        const descriptionInput = document.getElementById('groupDescription');
        const serverSelect = document.getElementById('groupServerSelect');
        
        nameInput.value = '';
        descriptionInput.value = '';
        
        if (group) {
            nameInput.value = group.name;
            nameInput.disabled = true;
            descriptionInput.value = group.description || '';
            
            Array.from(serverSelect.options).forEach(option => {
                option.selected = group.servers.includes(parseInt(option.value));
            });
        } else {
            nameInput.disabled = false;
        }

        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
    }

    getServerById(serverId) {
        // 이 메서드는 ServerManager에서 구현되어야 하며, 여기서는 인터페이스만 정의
        return null;
    }
} 