document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.onclick = function() {
            currentFilter = this.getAttribute('data-type');
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            buildNav();
        };
    });
    // Set 'All' as active by default
    document.querySelector('.filter-btn[data-type="all"]').classList.add('active');
});