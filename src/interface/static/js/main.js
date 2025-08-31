// In: src/interface/static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    const creditForm = document.getElementById('credit-form');
    if (!creditForm) return; // Stop if we're not on the add_user page

    // Keep chart variables in a scope accessible to the functions
    let probabilityChart = null;
    let positiveFeaturesChart = null;
    let negativeFeaturesChart = null;

    creditForm.addEventListener('submit', async function(event) {
        event.preventDefault();

        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const resultContainer = document.getElementById('result-container');

        // Show loading state
        resultContainer.style.display = 'none';
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Processing...
        `;

        const applicationData = {};
        const formData = new FormData(form);
        formData.forEach((value, key) => {
            const input = form.querySelector(`[name="${key}"]`);
            applicationData[key] = input.type === 'number' ? parseFloat(value) : value;
        });

        try {
            const response = await fetch('/predict/new_applicant', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(applicationData)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'An unknown server error occurred.');
            }

            renderResults(result);

        } catch (error) {
            console.error('Prediction Error:', error);
            resultContainer.style.display = 'block';
            resultContainer.innerHTML = `<p style="color: red;"><strong>Error:</strong> ${error.message}</p>`;
        } finally {
            // Reset button
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Predict Risk';
        }
    });

    function renderResults(result) {
        const resultContainer = document.getElementById('result-container');

        const resultHtml = `
            <div class="bg-white p-8 rounded-2xl shadow-lg border border-gray-200">
                <h2 class="text-3xl font-bold text-gray-900 text-center mb-8">Prediction Result</h2>
                <div class="grid md:grid-cols-3 gap-8 items-center">
                    <div class="md:col-span-1 text-center">
                        <canvas id="probability-chart" width="200" height="200"></canvas>
                        <div id="risk-level-text" class="text-2xl font-bold mt-4"></div>
                        <div class="text-gray-600">Probability of Default</div>
                    </div>
                    <div class="md:col-span-2">
                        <h3 class="text-xl font-semibold text-gray-800 mb-4">Key Factors Influencing Prediction</h3>
                        <div>
                            <h4 class="text-md font-medium text-red-600 mb-2">Factors Increasing Risk ↑</h4>
                            <canvas id="positive-features-chart"></canvas>
                        </div>
                        <div class="mt-6">
                            <h4 class="text-md font-medium text-green-600 mb-2">Factors Decreasing Risk ↓</h4>
                            <canvas id="negative-features-chart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        `;
        resultContainer.innerHTML = resultHtml;
        resultContainer.style.display = 'block';

        const riskLevelText = document.getElementById('risk-level-text');
        const probability = result.prediction_probability * 100;
        const riskLevel = probability > 10 ? 'High' : 'Low';
        const riskColor = riskLevel === 'High' ? '#ef4444' : '#22c55e';

        riskLevelText.textContent = `${riskLevel} Risk (${probability.toFixed(2)}%)`;
        riskLevelText.style.color = riskColor;

        if (probabilityChart) probabilityChart.destroy();
        if (positiveFeaturesChart) positiveFeaturesChart.destroy();
        if (negativeFeaturesChart) negativeFeaturesChart.destroy();

        const probCtx = document.getElementById('probability-chart').getContext('2d');
        probabilityChart = new Chart(probCtx, {
            type: 'doughnut',
            data: { datasets: [{ data: [probability, 100 - probability], backgroundColor: [riskColor, '#e5e7eb'], borderColor: ['#ffffff'], borderWidth: 4 }] },
            options: { responsive: true, cutout: '70%', plugins: { tooltip: { enabled: false }, legend: { display: false } } }
        });

        const impacts = result.feature_impacts;
        const sortedFeatures = Object.keys(impacts).sort((a, b) => Math.abs(impacts[b]) - Math.abs(impacts[a]));
        const top_n = 5;
        const positiveFeatures = sortedFeatures.filter(f => impacts[f] > 0).slice(0, top_n).reverse();
        const negativeFeatures = sortedFeatures.filter(f => impacts[f] < 0).slice(0, top_n).reverse();

        const createBarChart = (canvasId, features, color) => {
            const ctx = document.getElementById(canvasId).getContext('2d');
            return new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: features.map(f => f.replace(/_/g, ' ').replace(/mode/g, '').trim()),
                    datasets: [{ label: 'Impact', data: features.map(f => Math.abs(impacts[f])), backgroundColor: color, borderRadius: 4 }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    plugins: { legend: { display: false } },
                    scales: { x: { ticks: { display: false }, grid: { display: false }, border: { display: false } }, y: { grid: { display: false }, border: { display: false } } }
                }
            });
        };

        positiveFeaturesChart = createBarChart('positive-features-chart', positiveFeatures, 'rgba(239, 68, 68, 0.6)');
        negativeFeaturesChart = createBarChart('negative-features-chart', negativeFeatures, 'rgba(34, 197, 94, 0.6)');
    }
});