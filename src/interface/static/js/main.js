document.getElementById('credit-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const resultContainer = document.getElementById('result-container');
    const applicationData = {};
    formData.forEach((value, key) => {
        const input = form.querySelector(`[name="${key}"]`);
        applicationData[key] = input.type === 'number' ? parseFloat(value) : value;
    });

    resultContainer.innerHTML = '<p>Loading prediction...</p>';

    try {
        const response = await fetch('/predict/new_applicant', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(applicationData)
        });

        const result = await response.json();

        if (!response.ok) {
            let errorMessage = result.detail || 'An unknown server error occurred.';
            throw new Error(errorMessage);
        }

        // --- SUCCESS LOGIC ---
        const probability = (result.prediction_probability * 100).toFixed(2);
        const riskLevel = probability > 10 ? 'High' : 'Low';
        const riskColor = riskLevel === 'High' ? '#B82E2E' : '#22AA99';

        let explanationHtml = '<h4>Key Factors Influencing Prediction:</h4>';
        const impacts = result.feature_impacts;

        const sortedFeatures = Object.keys(impacts).sort((a, b) => Math.abs(impacts[b]) - Math.abs(impacts[a]));

        const top_n = 5;
        let positiveContributors = '';
        let negativeContributors = '';
        let posCount = 0;
        let negCount = 0;

        for (const feature of sortedFeatures) {
            if (impacts[feature] > 0 && posCount < top_n) {
                positiveContributors += `<li>${feature.replace(/_/g, ' ')} <span style="color: #B82E2E;">(increases risk)</span></li>`;
                posCount++;
            }
            if (impacts[feature] < 0 && negCount < top_n) {
                negativeContributors += `<li>${feature.replace(/_/g, ' ')} <span style="color: #22AA99;">(decreases risk)</span></li>`;
                negCount++;
            }
            if (posCount >= top_n && negCount >= top_n) break;
        }

        explanationHtml += '<div><strong>Factors Increasing Risk:</strong><ul>' + positiveContributors + '</ul></div>';
        explanationHtml += '<div><strong>Factors Decreasing Risk:</strong><ul>' + negativeContributors + '</ul></div>';

        resultContainer.innerHTML = `
            <h3>Prediction Result</h3>
            <p style="font-size: 1.2em;">
                Risk Level: <strong style="color: ${riskColor};">${riskLevel}</strong>
            </p>
            <p>
                <strong>Probability of Default:</strong> ${probability}%
            </p>
            ${explanationHtml}
        `;

    } catch (error) {
        console.error('Prediction Error:', error);
        resultContainer.innerHTML = `<p style="color: red;"><strong>Error:</strong> ${error.message}</p>`;
    }
});