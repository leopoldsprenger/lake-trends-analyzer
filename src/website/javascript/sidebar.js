let indexData = {};
let currentFilter = 'all';
let currentSearch = '';

async function loadIndex() {
    const response = await fetch('src/website/index.json');
    indexData = await response.json();
    buildNav();
    // Show first available graph
    const first = getFirstGraph(indexData.timeseries_graphs);
    if (first) showGraph(first.path);
}

function getFirstGraph(arr) {
    if (!arr || !arr.length) return null;
    return arr.find(item => filterMatch(item) && searchMatch(item));
}

function showGraph(path) {
    document.getElementById('loader').style.display = 'block';
    const img = document.getElementById('graph');
    img.style.opacity = 0;
    img.src = path;
    document.getElementById('title').textContent = formatFilename(path);
}

function hideLoader() {
    document.getElementById('loader').style.display = 'none';
    const img = document.getElementById('graph');
    img.style.opacity = 1;
}

document.addEventListener('DOMContentLoaded', () => {
    loadIndex();
});