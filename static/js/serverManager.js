export class ServerManager {
    constructor() {
        this.servers = JSON.parse(localStorage.getItem('proxyServers') || '[]');
    }

    saveServer(serverAddress) {
        if (!serverAddress) {
            alert('서버 주소를 입력하세요.');
            return false;
        }
        
        if (this.servers.includes(serverAddress)) {
            alert('이미 등록된 서버입니다.');
            return false;
        }
        
        this.servers.push(serverAddress);
        localStorage.setItem('proxyServers', JSON.stringify(this.servers));
        return true;
    }

    removeServer(server) {
        this.servers = this.servers.filter(s => s !== server);
        localStorage.setItem('proxyServers', JSON.stringify(this.servers));
    }

    getServers() {
        return this.servers;
    }
} 