export class UIManager {
    constructor() {
        this.currentView = 'dashboard';
    }

    updateServerList(servers, container, monitorSelect) {
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

        monitorSelect.innerHTML = '<option value="">서버 선택</option>';
        servers.forEach(server => {
            const option = document.createElement('option');
            option.value = server;
            option.textContent = server;
            monitorSelect.appendChild(option);
        });
    }

    updateSessionServerSelect(servers, select) {
        select.innerHTML = '<option value="">서버 선택</option>';
        servers.forEach(server => {
            const option = document.createElement('option');
            option.value = server;
            option.textContent = server;
            select.appendChild(option);
        });
    }

    updateResourceTable(data, resourceTable, cpuThreshold, memoryThreshold, selectedServer) {
        resourceTable.innerHTML = '';
        
        if (!data || Object.keys(data).length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = `<td colspan="11" class="text-center">모니터링 데이터가 없습니다. 모니터링을 시작해주세요.</td>`;
            resourceTable.appendChild(row);
            return;
        }
        
        const row = document.createElement('tr');
        const cpuClass = parseInt(data.cpu) >= cpuThreshold ? 'warning-cpu' : '';
        const memoryClass = parseInt(data.memory) >= memoryThreshold ? 'warning-memory' : '';
        
        row.innerHTML = `
            <td>${selectedServer}</td>
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

    updateSessionTable(data, sessionData) {
        sessionData.innerHTML = '';
        
        if (!data || data.length === 0) {
            sessionData.innerHTML = '<tr><td colspan="8" class="text-center">세션 데이터가 없습니다.</td></tr>';
            return;
        }
        
        data.forEach(session => {
            const row = document.createElement('tr');
            const formattedData = this.formatSessionData(session);
            
            row.innerHTML = `
                <td data-full-text="${formattedData.creationTime}">${formattedData.creationTime}</td>
                <td data-full-text="${formattedData.username}">${formattedData.username}</td>
                <td data-full-text="${formattedData.clientIP}">${formattedData.clientIP}</td>
                <td data-full-text="${formattedData.proxyIP}">${formattedData.proxyIP}</td>
                <td data-full-text="${formattedData.url}">${formattedData.url}</td>
                <td data-full-text="${formattedData.bytesReceived}">${formattedData.bytesReceived}</td>
                <td data-full-text="${formattedData.bytesSent}">${formattedData.bytesSent}</td>
                <td data-full-text="${formattedData.age}">${formattedData.age}</td>
            `;
            
            sessionData.appendChild(row);
        });
    }

    switchView(view) {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        document.querySelector(`[data-view="${view}"]`).classList.add('active');
        document.getElementById(this.currentView).classList.add('d-none');
        document.getElementById(view).classList.remove('d-none');
        this.currentView = view;
    }

    formatSessionData(session) {
        return {
            creationTime: session['Creation Time'] || 'N/A',
            username: session['User Name'] || 'N/A',
            clientIP: session['Client IP'] || 'N/A',
            proxyIP: session['Client Side MWG IP'] || 'N/A',
            url: session['URL'] || 'N/A',
            bytesReceived: session['CL Bytes Received'] || 'N/A',
            bytesSent: session['CL Bytes Sent'] || 'N/A',
            age: session['Age(seconds)'] || 'N/A'
        };
    }
} 