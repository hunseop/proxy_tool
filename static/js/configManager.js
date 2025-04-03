export class ConfigManager {
    async loadConfig() {
        try {
            const response = await fetch('/api/config');
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error:', error);
            return null;
        }
    }

    async saveConfig(config) {
        try {
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });
            const data = await response.json();

            if (data.status === 'success') {
                alert('설정이 저장되었습니다.');
                return true;
            } else {
                alert(`오류: ${data.message}`);
                return false;
            }
        } catch (error) {
            console.error('Error:', error);
            alert('설정 저장 중 오류가 발생했습니다.');
            return false;
        }
    }
} 