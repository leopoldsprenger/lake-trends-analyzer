function buildNav() {
    const nav = document.getElementById('nav');
    nav.innerHTML = '';

    createCollapsibleSection(nav, 'Timeseries Graphs', indexData.timeseries_graphs);
    createCollapsibleSection(nav, 'Seasonal Correlations', indexData.seasonal_correlations);
    createCorrelationSection(nav, indexData.correlation_graphs);
}

function createCollapsibleSection(parent, label, files) {
    const li = document.createElement('li');
    li.textContent = label;
    li.classList.add('toggle');

    const subList = document.createElement('ul');
    subList.classList.add('subfolder');
    parent.appendChild(li);
    parent.appendChild(subList);

    addCategory(subList, files);

    li.onclick = () => {
        subList.classList.toggle('collapsed');
        li.classList.toggle('collapsed-toggle');
    };
}

function createCorrelationSection(parent, data) {
    const li = document.createElement('li');
    li.textContent = 'Correlation Graphs';
    li.classList.add('toggle');

    const subList = document.createElement('ul');
    subList.classList.add('subfolder');
    parent.appendChild(li);
    parent.appendChild(subList);

    const sortedYVars = Object.keys(data).sort();
    for (const yVar of sortedYVars) {
        const sub = document.createElement('li');
        sub.textContent = formatLabel(yVar);
        sub.classList.add('toggle');

        const innerList = document.createElement('ul');
        innerList.classList.add('subfolder');
        subList.appendChild(sub);
        subList.appendChild(innerList);

        addCategory(innerList, data[yVar]);

        sub.onclick = () => {
            innerList.classList.toggle('collapsed');
            sub.classList.toggle('collapsed-toggle');
        };
    }

    li.onclick = () => {
        subList.classList.toggle('collapsed');
        li.classList.toggle('collapsed-toggle');
    };
}

function addCategory(parent, files) {
    files
        .filter(item => filterMatch(item) && searchMatch(item))
        .sort((a, b) => formatFilename(a.path).localeCompare(formatFilename(b.path)))
        .forEach(item => {
            const sub = document.createElement('li');
            sub.textContent = formatFilename(item.path);
            sub.onclick = (e) => {
                e.stopPropagation();
                showGraph(item.path);
            };
            parent.appendChild(sub);
        });
}