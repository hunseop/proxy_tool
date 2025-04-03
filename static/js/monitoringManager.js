export class MonitoringManager {
    constructor() {
        this.isMonitoring = false;
        this.cpuThreshold = 80;
        this.memoryThreshold = 75;
    }

    async startMonitoring(selectedServer, interval) {
        if (!selectedServer) {
            alert('서버를 선택해주세요.');
            return false;
        }

        try {
            const response = await fetch('/api/monitoring/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    hosts: [selectedServer],
                    interval: parseInt(interval)
                })
            });
            const data = await response.json();

            if (data.status === 'success') {
                this.isMonitoring = true;
                alert('모니터링이 시작되었습니다.');
                return true;
            } else {
                alert(`오류: ${data.message}`);
                return false;
            }
        } catch (error) {
            console.error('Error:', error);
            alert('모니터링 시작 중 오류가 발생했습니다.');
            return false;
        }
    }

    async stopMonitoring() {
        try {
            const response = await fetch('/api/monitoring/stop', {
                method: 'POST'
            });
            const data = await response.json();

            if (data.status === 'success') {
                this.isMonitoring = false;
                alert('모니터링이 중지되었습니다.');
                return true;
            } else {
                alert(`오류: ${data.message}`);
                return false;
            }
        } catch (error) {
            console.error('Error:', error);
            alert('모니터링 중지 중 오류가 발생했습니다.');
            return false;
        }
    }

    async fetchResourceData(selectedServer) {
        if (!this.isMonitoring) return null;

        try {
            const response = await fetch('/api/resources', {
                headers: {
                    'X-Monitor-Host': selectedServer
                }
            });
            return await response.json();
        } catch (error) {
            console.error('Error:', error);
            return null;
        }
    }

    setThresholds(cpu, memory) {
        this.cpuThreshold = cpu;
        this.memoryThreshold = memory;
    }

    getThresholds() {
        return {
            cpu: this.cpuThreshold,
            memory: this.memoryThreshold
        };
    }

    isActive() {
        return this.isMonitoring;
    }
} 