document.addEventListener('DOMContentLoaded', function() {
    let portfolioData = []; // To store the full user data

    const usersTableBody = document.getElementById('usersTableBody');
    const userCountSpan = document.getElementById('userCount');
    const userModal = document.getElementById('userModal');
    const userDetailsContent = document.getElementById('userDetailsContent');

    // --- INITIAL DATA LOADING ---
    async function loadPortfolio() {
        try {
            const response = await fetch('/track/portfolio');
            const data = await response.json();
            portfolioData = data.portfolio;
            renderTable(portfolioData);
        } catch (error) {
            console.error("Error loading portfolio:", error);
            usersTableBody.innerHTML = `<tr><td colspan="5" class="text-center p-4 text-red-500">Could not load user data.</td></tr>`;
        }
    }

    // --- RENDERING FUNCTIONS ---
    function renderTable(users) {
        usersTableBody.innerHTML = ''; // Clear existing rows
        if (users.length === 0) {
            usersTableBody.innerHTML = `<tr><td colspan="5" class="text-center p-4 text-gray-500">No users found.</td></tr>`;
            userCountSpan.textContent = '0 Users';
            return;
        }

        users.forEach(user => {
            const riskScore = user.risk_score.toFixed(0);
            const status = getRiskLevel(riskScore);
            const riskColor = getRiskColor(riskScore);
            const statusClass = getStatusClass(status);
            const initials = user.id.split('_')[1].charAt(0) + (user.id.split('_')[2] ? user.id.split('_')[2].charAt(0) : '');

            const row = `
                <tr class="hover:bg-gray-50 transition-colors">
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="flex items-center">
                            <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-semibold">
                                ${initials}
                            </div>
                            <div class="ml-4">
                                <div class="text-sm font-medium text-gray-900">${user.id.replace(/_/g, ' ')}</div>
                                <div class="text-sm text-gray-500">ID: ${user.id.split('_')[0]}</div>
                            </div>
                        </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="flex items-center">
                            <div class="w-16 bg-gray-200 rounded-full h-2 mr-3">
                                <div class="h-2 rounded-full" style="width: ${riskScore}%; background-color: ${riskColor};"></div>
                            </div>
                            <span class="text-sm font-medium" style="color: ${riskColor};">${riskScore}%</span>
                        </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${statusClass}">
                            ${status}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        ${user.last_updated}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div class="flex space-x-2">
                            <button onclick="viewUser('${user.id}')" class="text-finshield-blue hover:text-finshield-dark transition-colors">View</button>
                            <button onclick="updateUser('${user.id}')" class="text-green-600 hover:text-green-800 transition-colors">Update</button>
                        </div>
                    </td>
                </tr>
            `;
            usersTableBody.innerHTML += row;
        });
        userCountSpan.textContent = `${users.length} Users`;
    }

    // --- MODAL AND ACTION FUNCTIONS ---
    window.viewUser = function(userId) {
        const user = portfolioData.find(u => u.id === userId);
        if (!user) return;

        let detailsHtml = '<div class="grid md:grid-cols-2 gap-6">';
        for (const key in user) {
            if (['id', 'risk_score', 'status', 'last_updated'].includes(key)) continue;
            const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            detailsHtml += `
                <div class="flex justify-between text-sm py-2 border-b">
                    <span class="text-gray-600">${label}:</span>
                    <span class="font-medium text-gray-900">${user[key]}</span>
                </div>
            `;
        }
        detailsHtml += '</div>';

        userDetailsContent.innerHTML = detailsHtml;
        userModal.classList.remove('hidden');
        userModal.classList.add('flex');
    }

    window.updateUser = function(userId) {
        // For a hackathon, a simple prompt is a quick way to demo the update feature
        const newBill = prompt(`Update the Utility Bill for ${userId.replace(/_/g, ' ')}:`, '15000');
        if (newBill === null || isNaN(parseFloat(newBill))) {
            alert('Invalid amount entered.');
            return;
        }

        const updatedFeatures = { "UTILITY_BIL": parseFloat(newBill) };

        fetch(`/track/users/${userId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ features: updatedFeatures })
        })
        .then(response => response.json())
        .then(data => {
            if (data.new_probability_of_default !== undefined) {
                alert('User updated successfully! Reloading portfolio...');
                loadPortfolio(); // Reload the table to show the new score
            } else {
                throw new Error(data.detail || 'Failed to update user.');
            }
        })
        .catch(error => {
            console.error('Update Error:', error);
            alert(`Error: ${error.message}`);
        });
    }

    window.closeUserModal = function() {
        userModal.classList.add('hidden');
        userModal.classList.remove('flex');
    }

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