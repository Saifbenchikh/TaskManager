// GESTION DES ONGLETS
function showTab(event, tabId) {
    if(event) event.preventDefault();
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
    
    // GESTION VISIBILITÉ BOUTON TRI PROJETS
    const btnSort = document.getElementById('btnSortProjects');
    if (btnSort) {
        if (tabId === 'projets') {
            btnSort.classList.remove('d-none'); 
        } else {
            btnSort.classList.add('d-none');   
        }
    }

    localStorage.setItem('activeTab', tabId);
}

//  GESTION PROJETS 
document.addEventListener('shown.bs.collapse', function (e) {
    if (e.target.id.startsWith('collapseProjet')) {
        let openProjects = JSON.parse(localStorage.getItem('openProjects')) || [];
        if (!openProjects.includes(e.target.id)) {
            openProjects.push(e.target.id);
            localStorage.setItem('openProjects', JSON.stringify(openProjects));
        }
    }
});
document.addEventListener('hidden.bs.collapse', function (e) {
    if (e.target.id.startsWith('collapseProjet')) {
        let openProjects = JSON.parse(localStorage.getItem('openProjects')) || [];
        openProjects = openProjects.filter(id => id !== e.target.id);
        localStorage.setItem('openProjects', JSON.stringify(openProjects));
    }
});

//  GESTION DU MASQUAGE DES TÂCHES TERMINÉES 
function toggleProjectCompleted(projectId) {
    const isChecked = document.getElementById('switchCompleted' + projectId).checked;
    const container = document.getElementById('collapseProjet' + projectId);
    const doneTasks = container.querySelectorAll('.task-done');

    doneTasks.forEach(task => {
        if (isChecked) {
            task.classList.remove('d-none');
        } else {
            task.classList.add('d-none');
        }
    });
    localStorage.setItem('showDone_' + projectId, isChecked);
}

// AU CHARGEMENT DE LA PAGE
document.addEventListener('DOMContentLoaded', function() {

    const savedTab = localStorage.getItem('activeTab') || 'afaire';
    showTab(null, savedTab);

    // Restauration Projets Ouverts
    const openProjects = JSON.parse(localStorage.getItem('openProjects')) || [];
    openProjects.forEach(id => {
        const element = document.getElementById(id);
        const trigger = document.querySelector(`[data-bs-target="#${id}"]`);
        if (element && trigger) {
            element.classList.add('show');
            trigger.setAttribute('aria-expanded', 'true');
        }
    });

    // Restauration des interrupteurs
    const allSwitches = document.querySelectorAll('[id^="switchCompleted"]');
    allSwitches.forEach(switchEl => {
        const projectId = switchEl.id.replace('switchCompleted', '');
        const savedState = localStorage.getItem('showDone_' + projectId);
        if (savedState !== null) {
            switchEl.checked = (savedState === 'true');
        }
        toggleProjectCompleted(projectId);
    });

    //  GRAPHIQUES 
    const dataDiv = document.getElementById('statsData');
    if (!dataDiv) return;

    const danger = parseInt(dataDiv.getAttribute('data-danger'));
    const warning = parseInt(dataDiv.getAttribute('data-warning'));
    const primary = parseInt(dataDiv.getAttribute('data-primary'));
    const afaire = parseInt(dataDiv.getAttribute('data-afaire'));
    const terminees = parseInt(dataDiv.getAttribute('data-terminees'));

    const ctx1 = document.getElementById('chartUrgence').getContext('2d');
    new Chart(ctx1, {
        type: 'doughnut',
        data: {
            labels: ['Urgent', 'Important', 'Normal'],
            datasets: [{
                data: [danger, warning, primary],
                backgroundColor: ['#ef4444', '#f59e0b', '#4f46e5'],
                borderWidth: 0
            }]
        },
        options: { cutout: '70%', responsive: true, plugins: { legend: { position: 'bottom' } } }
    });

    const ctx2 = document.getElementById('chartStatut').getContext('2d');
    new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: ['À faire', 'Terminées'],
            datasets: [{
                label: 'Tâches',
                data: [afaire, terminees],
                backgroundColor: ['#6366f1', '#10b981'],
                borderRadius: 5
            }]
        },
        options: { scales: { y: { beginAtZero: true } }, plugins: { legend: { display: false } } }
    });
});

// FONCTIONS UTILES
function toggleDarkMode(event) {
    if(event) event.preventDefault();
    let body = document.body;
    let icon = document.getElementById('dark-icon');
    let text = document.getElementById('dark-text');
    if (body.getAttribute('data-theme') === 'dark') {
        body.setAttribute('data-theme', 'light');
        icon.classList.replace('fa-sun', 'fa-moon');
        text.innerText = "Mode Sombre";
        localStorage.setItem('theme', 'light');
    } else {
        body.setAttribute('data-theme', 'dark');
        icon.classList.replace('fa-moon', 'fa-sun');
        text.innerText = "Mode Clair";
        localStorage.setItem('theme', 'dark');
    }
}
if (localStorage.getItem('theme') === 'dark') toggleDarkMode();

function filtrerTaches() {
    let input = document.getElementById('searchInput').value.toLowerCase();
    let items = document.querySelectorAll('.search-item');
    items.forEach(item => {
        if (item.innerText.toLowerCase().includes(input)) item.classList.remove('d-none');
        else item.classList.add('d-none');
    });
}
function toggleSidebar() { document.getElementById('sidebar').classList.toggle('active'); }