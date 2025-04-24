
// Theme handling
function toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon();
}

function updateThemeIcon() {
    const button = document.querySelector('.theme-toggle');
    const currentTheme = document.body.getAttribute('data-theme') || 'dark';
    button.textContent = currentTheme === 'light' ? 'FunckMode deaktivieren' : 'FunckMode aktivieren';
}

document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.body.setAttribute('data-theme', savedTheme);
    updateThemeIcon();
});

// WebSocket connection
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
let ws = new WebSocket(protocol + '//' + window.location.host + '/ws');
let reconnectTimer;

function connect() {
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        const voiceUsersDiv = document.querySelector('.voice-users');
        const defaultAvatar = 'https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png';
        
        if (data.uptime) {
            document.querySelector('.uptime').textContent = data.uptime;
        }
        if (data.voice_users) {
            const newUsers = data.voice_users.length ? 
                data.voice_users.map(user => `
                    <div class="user-card" data-speaking="${user.is_speaking}">
                        <img src="${user.avatar_url}" class="user-avatar" onerror="this.src='${defaultAvatar}'"/>
                        ${user.is_muted ? '🔇' : '🎙️'}︱🏠 ${user.server}︱${user.channel}︱${user.name} 
                    </div>
                `).join('') : 
                '<p>Keine Nutzer in Voice-Channels</p>';

            voiceUsersDiv.innerHTML = newUsers;
        }
    };

    ws.onclose = function() {
        clearTimeout(reconnectTimer);
        reconnectTimer = setTimeout(() => {
            ws = new WebSocket(protocol + '//' + window.location.host + '/ws');
            connect();
        }, 1000);
    };
}

connect();
