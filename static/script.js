// GESTION DES ONGLETS
function showTab(tabId) {
    document.querySelectorAll('.tab-section').forEach(el => el.classList.add('d-none'));
    document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
    
    const target = document.getElementById('tab-' + tabId);
    target.classList.remove('d-none');
    
    // Rejouer l'animation quand on change d'onglet
    target.classList.remove('animate-stagger');
    void target.offsetWidth; // Force le navigateur à redessiner
    target.classList.add('animate-stagger');

    event.currentTarget.classList.add('active');
}

// RECHERCHE
function filtrerTaches() {
    let input = document.getElementById('searchInput').value.toLowerCase();
    let items = document.querySelectorAll('.search-item');
    items.forEach(item => {
        if (item.innerText.toLowerCase().includes(input)) item.classList.remove('d-none');
        else item.classList.add('d-none');
    });
}

// DARK MODE
function toggleDarkMode() {
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

// MOBILE SIDEBAR
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('active');
}

// --- INITIALISATION DES GRAPHIQUES (Chart.js) ---
document.addEventListener('DOMContentLoaded', function() {
    const dataDiv = document.getElementById('statsData');
    if (!dataDiv) return;

    // Récupération des chiffres envoyés par Python
    const danger = parseInt(dataDiv.getAttribute('data-danger'));
    const warning = parseInt(dataDiv.getAttribute('data-warning'));
    const primary = parseInt(dataDiv.getAttribute('data-primary'));
    const afaire = parseInt(dataDiv.getAttribute('data-afaire'));
    const terminees = parseInt(dataDiv.getAttribute('data-terminees'));

    // 1. Graphique CAMEMBERT (Urgences)
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

    // 2. Graphique BARRES (Statut Global)
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