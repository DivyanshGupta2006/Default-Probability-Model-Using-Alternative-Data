document.addEventListener('DOMContentLoaded', function() {
    let portfolioData = [];
    let currentUserForUpdate = null;

    const usersTableBody = document.getElementById('usersTableBody');
    const userCountSpan = document.getElementById('userCount');
    const userModal = document.getElementById('userModal');
    const userDetailsContent = document.getElementById('userDetailsContent');
    const updateModal = document.getElementById('updateModal');
    const updateUserForm = document.getElementById('updateUserForm');

    // --- INITIAL DATA LOADING ---
    async function loadPortfolio() {
        showLoading(true);
        try {
            const response = await fetch('/track/portfolio');
            if (!response.ok) throw new Error('Failed to fetch portfolio data.');
            const data = await response.json();
            portfolioData = data.portfolio || [];
            renderTable(portfolioData);
            updateStatistics(portfolioData);
        } catch (error) {
            console.error("Error loading portfolio:", error);
            showError(error.message);
        } finally {
            showLoading(false);
        }
    }

    // --- UI & RENDERING FUNCTIONS ---
    function renderTable(users) {
        usersTableBody.innerHTML = '';
        if (users.length === 0) {
            document.getElementById('noDataMessage').style.display = 'block';
            document.getElementById('tableContainer').style.display = 'none';
            return;
        }
        document.getElementById('noDataMessage').style.display = 'none';
        document.getElementById('tableContainer').style.display = 'block';

        users.forEach(user => {
            const riskScore = parseFloat(user.risk_score).toFixed(1);
            const riskLevel = getRiskLevel(riskScore);
            const riskColor = getRiskColor(riskScore);
            const statusClass = getStatusClass(riskLevel);
            const initials = getInitials(user.id);

            const row = `
                <tr class="hover:bg-gray-50">
                    <td class="px-6 py-4"><div class="flex items-center"><div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-semibold">${initials}</div><div class="ml-4"><div class="text-sm font-medium text-gray-900">${user.id.replace(/_/g, ' ')}</div><div class="text-sm text-gray-500">${user.id.split('_')[0]}</div></div></div></td>
                    <td class="px-6 py-4"><div class="flex items-center"><div class="w-16 bg-gray-200 rounded-full h-2 mr-3"><div class="h-2 rounded-full" style="width: ${riskScore}%; background-color: ${riskColor};"></div></div><span class="text-sm font-medium" style="color: ${riskColor};">${riskScore}%</span></div></td>
                    <td class="px-6 py-4"><span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${statusClass}">${riskLevel}</span></td>
                    <td class="px-6 py-4 text-sm text-gray-500">${user.last_updated}</td>
                    <td class="px-6 py-4 text-sm font-medium"><div class="flex space-x-2"><button onclick="viewUser('${user.id}')" class="text-finshield-blue hover:text-finshield-dark">View</button><button onclick="openUpdateModal('${user.id}')" class="text-green-600 hover:text-green-800">Update</button></div></td>
                </tr>`;
            usersTableBody.innerHTML += row;
        });
        userCountSpan.textContent = `${users.length} Users`;
    }

    // ... (Your other UI functions: updateStatistics, showLoading, showError) ...

    // --- MODAL AND ACTION FUNCTIONS ---
    window.viewUser = function(userId) { /* Your viewUser function */ };

    window.openUpdateModal = function(userId) {
        currentUserForUpdate = portfolioData.find(u => u.id === userId);
        if (!currentUserForUpdate) return;
        // Populate the update form with the user's current data
        document.getElementById('updateUtilityBill').value = currentUserForUpdate.UTILITY_BIL;
        document.getElementById('updateSmartCards').value = currentUserForUpdate.NO_OF_SMRT_CARD;
        document.getElementById('updateRechargeFreq').value = currentUserForUpdate.RCHRG_FRQ;
        document.getElementById('updateTruecaller').value = currentUserForUpdate.TRUECALR_FLAG;
        updateModal.classList.remove('hidden');
        updateModal.classList.add('flex');
    };

    window.closeUpdateModal = function() {
        updateModal.classList.add('hidden');
        updateModal.classList.remove('flex');
    };

    updateUserForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        const formData = new FormData(updateUserForm);
        const updatedFeatures = {};
        formData.forEach((value, key) => {
            // Convert to number if the original value was a number
            if (typeof currentUserForUpdate[key] === 'number' && value) {
                updatedFeatures[key] = parseFloat(value);
            } else if (value) {
                updatedFeatures[key] = value;
            }
        });

        try {
            const response = await fetch(`/track/users/${currentUserForUpdate.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ features: updatedFeatures })
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.detail);

            closeUpdateModal();
            loadPortfolio(); // Refresh the table with the new risk score
        } catch (error) {
            console.error('Update Error:', error);
            alert(`Update failed: ${error.message}`);
        }
    });

    // --- HELPER FUNCTIONS ---
    // ... (Your helper functions: getInitials, getRiskColor, getRiskLevel, getStatusClass) ...

    // --- INITIALIZE THE PAGE ---
    loadPortfolio();
});

    // --- HELPER FUNCTIONS ---
    function getRiskColor(score) {
        if (score < 30) return '#10b981'; // green
        if (score < 70) return '#f59e0b'; // yellow
        return '#ef4444'; // red
    }

    function getRiskLevel(score) {
        if (score < 30) return 'Approved';
        if (score < 70) return 'Under Review';
        return 'Rejected';
    }

    function getStatusClass(status) {
        switch (status.toLowerCase()) {
            case 'approved': return 'bg-green-100 text-green-800';
            case 'under review': return 'bg-yellow-100 text-yellow-800';
            case 'rejected': return 'bg-red-100 text-red-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    }

    // Initialize the page
    loadPortfolio();
});