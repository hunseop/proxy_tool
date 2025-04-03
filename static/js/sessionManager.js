export class SessionManager {
    async loadSessionData(server, search = '', isRefresh = false) {
        if (!server) {
            alert('선택된 서버가 없습니다.');
            return null;
        }

        let url = `/api/sessions/${server}`;
        if (search && !isRefresh) {
            url += `?search=${encodeURIComponent(search)}`;
        }

        try {
            const response = await fetch(url);
            return await response.json();
        } catch (error) {
            console.error('Error:', error);
            return null;
        }
    }

    formatSessionData(session) {
        return {
            creationTime: session['Creation Time'] || '-',
            username: session['User Name'] || '-',
            clientIP: session['Client IP'] || '-',
            proxyIP: session['Proxy IP'] || '-',
            url: session['URL'] || '-',
            bytesReceived: session['CL Bytes Received'] || '-',
            bytesSent: session['CL Bytes Sent'] || '-',
            age: session['Age(seconds)'] || '-'
        };
    }
} 