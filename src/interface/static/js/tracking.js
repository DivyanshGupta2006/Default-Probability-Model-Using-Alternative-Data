document.addEventListener('DOMContentLoaded', function () {
    let portfolioData = [];
    let currentUserId = null;
    let historyChart = null;

    // --- Element References ---
    const usersTableBody = document.getElementById('usersTableBody');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const tableContainer = document.getElementById('tableContainer');
    const noDataMessage = document.getElementById('noDataMessage');
    const userSearchInput = document.getElementById('userSearch');
    const riskFilterSelect = document.getElementById('riskFilter');
    const statusFilterSelect = document.getElementById('statusFilter');

    // Modal elements
    const userModal = document.getElementById('userModal');
    const updateModal = document.getElementById('updateModal');
    const historyModal = document.getElementById('historyModal');
    const updateUserForm = document.getElementById('updateUserForm');

    // --- DEBOUNCE FUNCTION ---
    let debounceTimer;
    const debounce = (callback, time) => {
        window.clearTimeout(debounceTimer);
        debounceTimer = window.setTimeout(callback, time);
    };

    // --- EVENT LISTENERS ---
    userSearchInput.addEventListener('input', () => debounce(loadPortfolio, 500));
    riskFilterSelect.addEventListener('change', loadPortfolio);
    statusFilterSelect.addEventListener('change', loadPortfolio);
    updateUserForm.addEventListener('submit', handleUpdateUser);

    // --- UI & RENDERING ---
    function showLoading(isLoading) {
        loadingIndicator.style.display = isLoading ? 'block' : 'none';
        if (isLoading) {
            tableContainer.style.display = 'none';
            noDataMessage.style.display = 'none';
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
                    <td class="px-6 py-4 whitespace-nowrap"><div class="flex items-center"><div class="w-20 bg-gray-200 rounded-full h-2 mr-3 risk-bar"><div class="h-2 rounded-full risk-fill" style="width: ${riskScore}%; background-color: ${riskColor};"></div></div><span class="text-sm font-medium" style="color: ${riskColor};">${riskScore}%</span></div></td>
                    <td class="px-6 py-4 whitespace-nowrap"><span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${statusClass}">${riskCategory.charAt(0).toUpperCase() + riskCategory.slice(1)}</span></td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${user.last_updated}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium"><div class="flex space-x-2">
                        <button onclick="openUserModal('${user.id}')" class="text-finshield-blue hover:text-finshield-dark">View</button>
                        <button onclick="openUpdateModal('${user.id}')" class="text-green-600 hover:text-green-800">Update</button>
                    </div></td>
                </tr>`;
            usersTableBody.innerHTML += row;
        });
        document.getElementById('userCount').textContent = `${users.length} Users`;
    }

    // --- HELPER FUNCTIONS ---
    function getInitials(name) { if (!name) return '??'; const p = name.split(' '); return p.length > 1 ? (p[0][0] + p[p.length - 1][0]).toUpperCase() : name.substring(0, 2).toUpperCase(); }
    function getRiskColor(c) { return { 'low': '#10b981', 'medium': '#f59e0b', 'high': '#ef4444' }[c] || '#6b7280'; }
    function getStatusClass(c) { return { 'low': 'bg-green-100 text-green-800', 'medium': 'bg-yellow-100 text-yellow-800', 'high': 'bg-red-100 text-red-800' }[c] || 'bg-gray-100 text-gray-800'; }

    // --- DATA LOADING ---
    async function loadPortfolio() {
        showLoading(true);
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

    // --- MODAL & ACTION HANDLERS ---
    window.openUserModal = async (userId) => {
        currentUserId = userId;
        const modalContent = document.getElementById('userDetailsContent');
        modalContent.innerHTML = '<div class="text-center py-10">Loading details...</div>';
        userModal.classList.remove('hidden');
        userModal.classList.add('flex');

        try {
            const response = await fetch(`/track/users/${userId}`);
            if (!response.ok) throw new Error('Could not fetch user details.');
            const data = await response.json();
            renderUserDetails(data);
        } catch (error) {
            modalContent.innerHTML = `<p class="text-red-500 text-center">${error.message}</p>`;
        }
    };

    function renderUserDetails(data) {
        const contentEl = document.getElementById('userDetailsContent');
        document.getElementById('modalUserTitle').textContent = `Details for ${data.user_info.full_name}`;

        const positiveImpacts = Object.entries(data.latest_assessment.feature_impacts || {}).filter(([_, val]) => val > 0).slice(0, 5);
        const negativeImpacts = Object.entries(data.latest_assessment.feature_impacts || {}).filter(([_, val]) => val < 0).slice(0, 5);

        contentEl.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="md:col-span-1 space-y-4">
                    <h4 class="text-lg font-semibold text-gray-800 border-b pb-2">User Information</h4>
                    <p><strong>ID:</strong> ${data.user_info.id}</p>
                    <p><strong>Email:</strong> ${data.user_info.email || 'N/A'}</p>
                    <p><strong>Status:</strong> <span class="capitalize p-1 rounded ${getStatusClass(data.latest_assessment.risk_category)}">${data.user_info.status}</span></p>
                    <p><strong>Member Since:</strong> ${data.user_info.created_at}</p>
                    <p><strong>Last Assessed:</strong> ${data.latest_assessment.assessed_at}</p>
                </div>
                <div class="md:col-span-2 space-y-4">
                    <h4 class="text-lg font-semibold text-gray-800 border-b pb-2">Risk Assessment History</h4>
                    <canvas id="historyChartCanvas"></canvas>
                </div>
            </div>
             <div class="mt-6">
                <h4 class="text-lg font-semibold text-gray-800 border-b pb-2">Top 5 Feature Impacts (Latest Assessment)</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
                    <div>
                        <h5 class="font-medium text-red-600 mb-2">Factors Increasing Risk ↑</h5>
                        <ul class="space-y-1 text-sm text-gray-700">${positiveImpacts.map(([key, val]) => `<li>${key}: <span class="font-semibold">${val.toFixed(3)}</span></li>`).join('') || '<li>None</li>'}</ul>
                    </div>
                     <div>
                        <h5 class="font-medium text-green-600 mb-2">Factors Decreasing Risk ↓</h5>
                        <ul class="space-y-1 text-sm text-gray-700">${negativeImpacts.map(([key, val]) => `<li>${key}: <span class="font-semibold">${val.toFixed(3)}</span></li>`).join('') || '<li>None</li>'}</ul>
                    </div>
                </div>
            </div>
        `;

        if (historyChart) historyChart.destroy();
        const ctx = document.getElementById('historyChartCanvas').getContext('2d');
        historyChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.assessment_history.map(h => h.assessed_at),
                datasets: [{
                    label: 'Default Probability',
                    data: data.assessment_history.map(h => parseFloat(h.prediction_probability) * 100),
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.1
                }]
            },
            options: { scales: { y: { beginAtZero: true, max: 100, ticks: { callback: value => value + '%' } } } }
        });
    }

    window.closeUserModal = () => userModal.classList.add('hidden');
    window.closeUpdateModal = () => updateModal.classList.add('hidden');
    window.closeHistoryModal = () => historyModal.classList.add('hidden');

    window.openUpdateModal = (userId) => {
        currentUserId = userId;
        const user = portfolioData.find(u => u.id === userId);
        if (user) {
            // Hide any previous error messages
            document.getElementById('updateFormError').classList.add('hidden');

            // Populate form fields
            updateUserForm.elements['utility_bil'].value = user.utility_bil || '';
            updateUserForm.elements['no_of_smrt_card'].value = user.no_of_smrt_card || '';
            updateUserForm.elements['rchrg_frq'].value = user.rchrg_frq || '';
            updateUserForm.elements['truecalr_flag'].value = user.truecalr_flag || '';

            // Populate NEW fields
            updateUserForm.elements['gst_fil_def'].value = user.gst_fil_def || '';
            updateUserForm.elements['reg_veh_challan'].value = user.reg_veh_challan || '';
            updateUserForm.elements['ecom_shop_return'].value = user.ecom_shop_return || '';

            document.getElementById('updateReason').value = '';
            updateModal.classList.remove('hidden');
            updateModal.classList.add('flex');
        } else {
            alert('User data not found.');
        }
    };

    async function handleUpdateUser(event) {
        event.preventDefault();

        const submitBtn = updateUserForm.querySelector('button[type="submit"]');
        const errorDiv = document.getElementById('updateFormError');
        const errorMessageSpan = document.getElementById('updateFormErrorMessage');

        // Reset UI states
        errorDiv.classList.add('hidden');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Updating...';

        const formData = new FormData(updateUserForm);
        const updatedData = {};
        // Collect only non-empty fields to send to the backend
        formData.forEach((value, key) => {
            if (value !== null && value.trim() !== '') {
                const input = updateUserForm.elements[key];
                if (input.type === 'number' && value.trim() !== '') {
                    updatedData[key.toUpperCase()] = parseFloat(value); // Convert to uppercase to match Pydantic model
                } else {
                    updatedData[key.toUpperCase()] = value;
                }
            }
        });

        try {
            const response = await fetch(`/track/users/${currentUserId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updatedData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to update user. Please try again.');
            }

            // If successful, close the modal and refresh the portfolio table
            closeUpdateModal();
            loadPortfolio();

        } catch (error) {
            console.error("Update Error:", error);
            errorMessageSpan.textContent = error.message;
            errorDiv.classList.remove('hidden');
        } finally {
            // Always re-enable the button
            submitBtn.disabled = false;
            submitBtn.textContent = 'Update User';
        }
    }

    // --- INITIALIZE ---
    loadPortfolio();
});

