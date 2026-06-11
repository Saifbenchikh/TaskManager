// SYSTÈME GÉNÉRATEUR DE TOASTS EN JS

// ==========================================================
// CHATBOT ASSISTANT VIRTUEL - LOGIQUE
// ==========================================================

function toggleChat() {
    const chatWindow = document.getElementById('chatbotWindow');
    chatWindow.classList.toggle('active');
    if(chatWindow.classList.contains('active')) {
        document.getElementById('chatInput').focus();
    }
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendChatMessage();
    }
}

function createMessageElement(text, isUser = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    msgDiv.textContent = text;
    return msgDiv;
}

function showTypingIndicator() {
    const messagesDiv = document.getElementById('chatbotMessages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = '<span></span><span></span><span></span>';
    messagesDiv.appendChild(typingDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function hideTypingIndicator() {
    const typingDiv = document.getElementById('typingIndicator');
    if (typingDiv) {
        typingDiv.remove();
    }
}

async function sendChatMessage() {
    const inputEl = document.getElementById('chatInput');
    const message = inputEl.value.trim();
    if (!message) return;

    const messagesDiv = document.getElementById('chatbotMessages');

    messagesDiv.appendChild(createMessageElement(message, true));
    inputEl.value = '';
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    showTypingIndicator();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();
        
        setTimeout(() => {
            hideTypingIndicator();
            messagesDiv.appendChild(createMessageElement(data.reply, false));
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            if (data.action === 'reload') {
                setTimeout(() => window.location.reload(), 2500);
            }
        }, 800); 
        
    } catch (error) {
        console.error('Erreur API Chatbot:', error);
        hideTypingIndicator();
        messagesDiv.appendChild(createMessageElement("Oups, je rencontre un problème de connexion au serveur.", false));
    }
}


function createToast(message, type = 'success') {
    let container = document.getElementById('toast-container-custom');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container-custom';
        container.className = 'toast-container-custom';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast-custom ${type}`;
    
    const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
    const title = type === 'success' ? 'Succès' : 'Une erreur est survenue';
    const duration = 4000; 

    toast.innerHTML = `
        <div class="toast-icon"><i class="fas ${icon}"></i></div>
        <div class="toast-body">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        </div>
        <div class="toast-progress" style="animation-duration: ${duration}ms"></div>
    `;

    container.appendChild(toast);

    const timeout = setTimeout(() => {
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// MANAGEMENT DES ONGLETS PRINCIPAUX (INDEX)
function showTab(event, tabId) {
    if(event) event.preventDefault();
    if(!document.getElementById('tab-' + tabId)) return; 
    
    document.querySelectorAll('.tab-section').forEach(el => el.classList.add('d-none'));
    document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
    
    const target = document.getElementById('tab-' + tabId);
    if(target) {
        target.classList.remove('d-none');
        target.classList.remove('animate-stagger');
        void target.offsetWidth; 
        target.classList.add('animate-stagger');
    }

    const activeLink = document.querySelector(`.nav-link[onclick*="'${tabId}'"]`);
    if (activeLink) activeLink.classList.add('active');
    
    const btnSort = document.getElementById('btnSortProjects');
    if (btnSort) {
        if (tabId === 'projets') btnSort.classList.remove('d-none'); 
        else btnSort.classList.add('d-none');   
    }
    localStorage.setItem('activeTab', tabId);
}

// MANAGEMENT EXPANSION DES ACCORDÉONS PROJETS
document.addEventListener('shown.bs.collapse', function (e) {
    if (e.target.id && e.target.id.startsWith('collapseProjet')) {
        let openProjects = JSON.parse(localStorage.getItem('openProjects')) || [];
        if (!openProjects.includes(e.target.id)) {
            openProjects.push(e.target.id);
            localStorage.setItem('openProjects', JSON.stringify(openProjects));
        }
    }
});
document.addEventListener('hidden.bs.collapse', function (e) {
    if (e.target.id && e.target.id.startsWith('collapseProjet')) {
        let openProjects = JSON.parse(localStorage.getItem('openProjects')) || [];
        openProjects = openProjects.filter(id => id !== e.target.id);
        localStorage.setItem('openProjects', JSON.stringify(openProjects));
    }
});

function toggleProjectCompleted(projectId) {
    const el = document.getElementById('switchCompleted' + projectId);
    if(!el) return;
    const isChecked = el.checked;
    const container = document.getElementById('collapseProjet' + projectId);
    if(!container) return;
    const doneTasks = container.querySelectorAll('.task-done');
    doneTasks.forEach(task => {
        if (isChecked) task.classList.remove('d-none');
        else task.classList.add('d-none');
    });
    localStorage.setItem('showDone_' + projectId, isChecked);
}

// INITIALISATION DOM ET DES CHARTS
document.addEventListener('DOMContentLoaded', function() {
    const savedTab = localStorage.getItem('activeTab') || 'afaire';
    showTab(null, savedTab);

    const openProjects = JSON.parse(localStorage.getItem('openProjects')) || [];
    openProjects.forEach(id => {
        const element = document.getElementById(id);
        const trigger = document.querySelector(`[data-bs-target="#${id}"]`);
        if (element && trigger) {
            element.classList.add('show');
            trigger.setAttribute('aria-expanded', 'true');
        }
    });

    const allSwitches = document.querySelectorAll('[id^="switchCompleted"]');
    allSwitches.forEach(switchEl => {
        const projectId = switchEl.id.replace('switchCompleted', '');
        const savedState = localStorage.getItem('showDone_' + projectId);
        if (savedState !== null) switchEl.checked = (savedState === 'true');
        toggleProjectCompleted(projectId);
    });

    if(!window.Chart) return;
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.font.weight = '500';
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(17, 24, 39, 0.95)';
    Chart.defaults.plugins.tooltip.padding = 14;
    Chart.defaults.plugins.tooltip.cornerRadius = 12;

    const dataDiv = document.getElementById('statsData');
    if (!dataDiv) return; 

    const danger = parseInt(dataDiv.getAttribute('data-danger')) || 0;
    const warning = parseInt(dataDiv.getAttribute('data-warning')) || 0;
    const primary = parseInt(dataDiv.getAttribute('data-primary')) || 0;
    
    const radarLabels = JSON.parse(dataDiv.getAttribute('data-radar-labels') || '[]');
    const radarData = JSON.parse(dataDiv.getAttribute('data-radar-data') || '[]');
    const lineLabels = JSON.parse(dataDiv.getAttribute('data-line-labels') || '[]');
    const lineData = JSON.parse(dataDiv.getAttribute('data-line-data') || '[]');

    const ctx1 = document.getElementById('chartUrgence');
    if(ctx1) {
        new Chart(ctx1.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Urgent', 'Important', 'Normal'],
                datasets: [{
                    data: [danger, warning, primary],
                    backgroundColor: ['#ef4444', '#f59e0b', '#4f46e5'],
                    borderWidth: 0,
                    hoverOffset: 6
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, cutout: '78%', plugins: { legend: { position: 'bottom', labels: { usePointStyle: true, padding: 25 } } } }
        });
    }

    const ctxRadar = document.getElementById('chartRadar');
    if(ctxRadar) {
        new Chart(ctxRadar.getContext('2d'), {
            type: 'radar',
            data: {
                labels: radarLabels.length > 0 ? radarLabels : ['Aucun projet'],
                datasets: [{
                    label: 'Volume tâches',
                    data: radarData.length > 0 ? radarData : [0],
                    backgroundColor: 'rgba(79, 70, 229, 0.12)',
                    borderColor: '#4f46e5',
                    borderWidth: 2,
                    pointBackgroundColor: '#ffffff',
                    pointBorderColor: '#4f46e5',
                    pointRadius: 4
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { r: { beginAtZero: true, ticks: { display: false }, grid: { color: 'rgba(156, 163, 175, 0.15)' }, angleLines: { color: 'rgba(156, 163, 175, 0.15)' } } }, plugins: { legend: { display: false } } }
        });
    }

    const ctxLine = document.getElementById('chartLine');
    if(ctxLine) {
        new Chart(ctxLine.getContext('2d'), {
            type: 'line',
            data: {
                labels: lineLabels.length > 0 ? lineLabels : ['Aucune date'],
                datasets: [{
                    label: 'Tâches',
                    data: lineData.length > 0 ? lineData : [0],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.08)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.38,
                    pointRadius: 2,
                    pointHoverRadius: 6
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, ticks: { stepSize: 1 }, grid: { color: 'rgba(156, 163, 175, 0.08)' } }, x: { grid: { display: false } } }, plugins: { legend: { display: false } } }
        });
    }
});

// THEME ENGINE
function applyTheme(theme) {
    const body = document.body;
    const icon = document.getElementById("dark-icon");
    const text = document.getElementById("dark-text");

    body.setAttribute("data-theme", theme);
    body.setAttribute("data-bs-theme", theme);
    localStorage.setItem("theme", theme);

    const isDark = theme === "dark";

    if (icon) {
        icon.classList.remove("fa-sun", "fa-moon");
        icon.classList.add(isDark ? "fa-sun" : "fa-moon");
    }

    if (text) {
        text.textContent = isDark ? "Mode Clair" : "Mode Sombre";
    }

    if (window.Chart) {
        Chart.defaults.color = isDark ? "#E6EDF3" : "#111827";
        Chart.defaults.borderColor = isDark ? "rgba(255,255,255,.08)" : "rgba(0,0,0,.08)";
    }
}

function toggleDarkMode(event) {
    if (event) event.preventDefault();
    const currentTheme = document.body.getAttribute("data-theme") || "light";
    const nextTheme = currentTheme === "dark" ? "light" : "dark";
    applyTheme(nextTheme);
}

document.addEventListener("DOMContentLoaded", function () {
    const savedTheme = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    applyTheme(savedTheme || (prefersDark ? "dark" : "light"));
});

function filtrerTaches() {
    let input = document.getElementById('searchInput').value.toLowerCase();
    document.querySelectorAll('.search-item').forEach(item => {
        if (item.innerText.toLowerCase().includes(input)) item.classList.remove('d-none');
        else item.classList.add('d-none');
    });
}
function toggleSidebar() { document.getElementById('sidebar').classList.toggle('active'); }

// ==========================================================
// NAVIGATION ONGLETS PROFIL
// ==========================================================
function showProfileTab(event, tabId) {
    if(event) event.preventDefault();
    document.querySelectorAll('.profile-tab-section').forEach(el => el.classList.add('d-none'));
    document.querySelectorAll('.settings-nav-item').forEach(el => el.classList.remove('active'));
    
    const target = document.getElementById('ptab-' + tabId);
    if(target) {
        target.classList.remove('d-none');
    }
    
    if(event && event.currentTarget) {
        event.currentTarget.classList.add('active');
    }
}