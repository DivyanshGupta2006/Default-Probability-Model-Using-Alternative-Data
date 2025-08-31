document.addEventListener('DOMContentLoaded', function() {
    let portfolioData = [];

    const usersTableBody = document.getElementById('usersTableBody');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const tableContainer = document.getElementById('tableContainer');
    const noDataMessage = document.getElementById('noDataMessage');

    // --- UI & RENDERING FUNCTIONS ---

    // This function controls the visibility of the loading spinner and the table.
    // This is the core of the fix.
    function showLoading(isLoading) {
        if (isLoading) {
            loadingIndicator.style.display = 'block';
            tableContainer.style.display = 'none';
            noDataMessage.style.display = 'none';
        } else {
            loadingIndicator.style.display = 'none';
        }
    }

    // This function updates the statistic cards at the top of the page.
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
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="flex items-center">
                            <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-semibold">${initials}</div>
                            <div class="ml-4">
                                <div class="text-sm font-medium text-gray-900">${user.full_name}</div>
                                <div class="text-sm text-gray-500">${user.id}</div>
                            </div>
                        </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="flex items-center">
                            <div class="w-20 bg-gray-200 rounded-full h-2 mr-3">
                                <div class="h-2 rounded-full" style="width: ${riskScore}%; background-color: ${riskColor};"></div>
                            </div>
                            <span class="text-sm font-medium" style="color: ${riskColor};">${riskScore}%</span>
                        </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${statusClass}">${riskCategory.charAt(0).toUpperCase() + riskCategory.slice(1)} Risk</span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${user.last_updated}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div class="flex space-x-2">
                            <button class="text-finshield-blue hover:text-finshield-dark">View</button>
                            <button class="text-green-600 hover:text-green-800">Update</button>
                        </div>
                    </td>
                </tr>`;
            usersTableBody.innerHTML += row;
        });
        document.getElementById('userCount').textContent = `${users.length} Users`;
    }

    // --- HELPER FUNCTIONS ---
    function getInitials(name) {
        if (!name) return '??';
        const parts = name.split(' ');
        if (parts.length > 1) {
            return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
        }
        return name.substring(0, 2).toUpperCase();
    }

    function getRiskColor(category) {
        switch (category) {
            case 'low': return '#10b981'; // green
            case 'medium': return '#f59e0b'; // yellow
            case 'high': return '#ef4444'; // red
            default: return '#6b7280'; // gray
        }
    }

    function getStatusClass(category) {
        switch (category) {
            case 'low': return 'bg-green-100 text-green-800';
            case 'medium': return 'bg-yellow-100 text-yellow-800';
            case 'high': return 'bg-red-100 text-red-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    }

    // --- INITIAL DATA LOADING ---
    async function loadPortfolio() {
        showLoading(true); // Now this function exists and will show the spinner
        try {
            const response = await fetch('/track/portfolio');
            if (!response.ok) throw new Error('Failed to fetch portfolio data.');
            const data = await response.json();
            portfolioData = data.portfolio || [];
            renderTable(portfolioData);
            updateStatistics(portfolioData); // This will update the cards
        } catch (error) {
            console.error("Error loading portfolio:", error);
            noDataMessage.innerHTML = `<p class="text-red-500">${error.message}</p>`;
            noDataMessage.style.display = 'block';
        } finally {
            showLoading(false); // This ensures the spinner is hidden after loading
        }
    }

    // --- INITIALIZE THE PAGE ---
    loadPortfolio();
});