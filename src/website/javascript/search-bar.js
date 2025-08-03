document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('search-input').addEventListener('input', function() {
        currentSearch = this.value;
        buildNav();
    });
});

// Utility functions for search/filter
function filterMatch(item) {
    if (currentFilter === 'all') return true;
    return (item.csv_source || '').toLowerCase() === currentFilter;
}

function searchMatch(item) {
    if (!currentSearch) return true;
    const label = formatFilename(item.path).toLowerCase();
    return label.includes(currentSearch.toLowerCase());
}

function formatFilename(path) {
    const parts = path.split('/');
    const filename = parts[parts.length - 1].replace('.png', '');
    return formatLabel(filename);
}

function formatLabel(text) {
    return text.replace(/_/g, ' ').replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}