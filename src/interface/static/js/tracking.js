document.addEventListener('DOMContentLoaded', function() {
    let portfolioData = []; // This will hold the currently displayed data

    // --- Element References ---
    const usersTableBody = document.getElementById('usersTableBody');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const tableContainer = document.getElementById('tableContainer');
    const noDataMessage = document.getElementById('noDataMessage');

    // Filter Elements
    const userSearchInput = document.getElementById('userSearch');
    const riskFilterSelect = document.getElementById('riskFilter');
    const statusFilterSelect = document.getElementById('statusFilter');

    // --- DEBOUNCE FUNCTION for search input ---
    let debounceTimer;
    const debounce = (callback, time) => {
        window.clearTimeout(debounceTimer);
        debounceTimer = window.setTimeout(callback, time);
    };

    // --- EVENT LISTENERS for filters ---
    userSearchInput.addEventListener('input', () => debounce(loadPortfolio, 500));
    riskFilterSelect.addEventListener('change', loadPortfolio);
    statusFilterSelect.addEventListener('change', loadPortfolio);

    // --- UI & RENDERING FUNCTIONS ---
    function showLoading(isLoading) {
        if (isLoading) {
            loadingIndicator.style.display = 'block';
            tableContainer.style.display = 'none';
            noDataMessage.style.display = 'none';
        } else {
            loadingIndicator.style.display = 'none';
        }
    }

    function updateStatistics(users) {
        document.getElementById('totalUsers').textContent = users.length;
        document.getElementById('lowRiskUsers').textContent = users.filter(u => u.risk_category === 'low').length;
        document.getElementById('mediumRiskUsers').textContent = users.filter(u => u.risk_category === 'medium').length;
        document.getElementById('highRiskUsers').textContent = users.filter(u => u.risk_category === 'high').length;
    }

    function renderTable(users) {
        usersTableBody.innerHTML = '';
        if (users.length === 0) {
            noDataMessage.style.display = 'block';
            tableContainer.style.display = 'none';
            return;
        }
        noDataMessage.style.display = 'none';
        tableContainer.style.display = 'block';

        users.forEach(user => {
            const riskScore = parseFloat(user.risk_score).toFixed(1);
            const riskCategory = user.risk_category;
            const riskColor = getRiskColor(riskCategory);
            const statusClass = getStatusClass(riskCategory);
            const initials = getInitials(user.full_name);

            const row = `
                <tr class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap"><div class="flex items-center"><div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-semibold">${initials}</div><div class="ml-4"><div class="text-sm font-medium text-gray-900">${user.full_name}</div><div class="text-sm text-gray-500">${user.id}</div></div></div></td>
                    <td class="px-6 py-4 whitespace-nowrap"><div class="flex items-center"><div class="w-20 bg-gray-200 rounded-full h-2 mr-3"><div class="h-2 rounded-full" style="width: ${riskScore}%; background-color: ${riskColor};"></div></div><span class="text-sm font-medium" style="color: ${riskColor};">${riskScore}%</span></div></td>
                    <td class="px-6 py-4 whitespace-nowrap"><span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${statusClass}">${riskCategory.charAt(0).toUpperCase() + riskCategory.slice(1)}</span></td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${user.last_updated}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium"><div class="flex space-x-2"><button class="text-finshield-blue hover:text-finshield-dark">View</button><button class="text-green-600 hover:text-green-800">Update</button></div></td>
                </tr>`;
            usersTableBody.innerHTML += row;
        });
        document.getElementById('userCount').textContent = `${users.length} Users`;
    }

    // --- HELPER FUNCTIONS ---
    function getInitials(name) { if (!name) return '??'; const p = name.split(' '); return p.length > 1 ? (p[0][0] + p[p.length - 1][0]).toUpperCase() : name.substring(0, 2).toUpperCase(); }
    function getRiskColor(c) { return {'low':'#10b981','medium':'#f59e0b','high':'#ef4444'}[c] || '#6b7280'; }
    function getStatusClass(c) { return {'low':'bg-green-100 text-green-800','medium':'bg-yellow-100 text-yellow-800','high':'bg-red-100 text-red-800'}[c] || 'bg-gray-100 text-gray-800'; }

    // --- DATA LOADING & ACTIONS ---
    async function loadPortfolio() {
        showLoading(true);

        // Build the query string from the filter inputs
        const params = new URLSearchParams();
        if (userSearchInput.value) params.append('search', userSearchInput.value);
        if (riskFilterSelect.value) params.append('risk_level', riskFilterSelect.value);
        if (statusFilterSelect.value) params.append('status', statusFilterSelect.value);
        const queryString = params.toString();

        try {
            const response = await fetch(`/track/portfolio?${queryString}`);
            if (!response.ok) throw new Error('Failed to fetch portfolio data.');
            const data = await response.json();
            portfolioData = data.portfolio || [];
            renderTable(portfolioData);
            updateStatistics(portfolioData);
        } catch (error) {
            console.error("Error loading portfolio:", error);
            noDataMessage.innerHTML = `<p class="text-red-500">${error.message}</p>`;
            noDataMessage.style.display = 'block';
        } finally {
            showLoading(false);
        }
    }

    // --- Attaching functions to the window object to make them accessible from HTML onclick ---
    window.clearFilters = function() {
        userSearchInput.value = '';
        riskFilterSelect.value = '';
        statusFilterSelect.value = '';
        loadPortfolio(); // Reload data with cleared filters
    }

    // The "Refresh" button in the image seems to mean "clear filters and refresh"
    window.refreshData = function() {
        clearFilters();
    }

    window.exportData = function() {
        if (portfolioData.length === 0) {
            alert("No data to export.");
            return;
        }

        const headers = Object.keys(portfolioData[0]);
        const csvRows = [headers.join(',')]; // Header row

        portfolioData.forEach(row => {
            const values = headers.map(header => {
                const escaped = ('' + row[header]).replace(/"/g, '""'); // Escape double quotes
                return `"${escaped}"`; // Quote all fields
            });
            csvRows.push(values.join(','));
        });

        const csvString = csvRows.join('\\n');
        const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", `finshield_portfolio_${new Date().toISOString().slice(0,10)}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    // --- INITIALIZE THE PAGE ---
    loadPortfolio();
});