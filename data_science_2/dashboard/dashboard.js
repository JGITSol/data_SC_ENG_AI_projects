document.getElementById('predict-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const form = e.target;
    const features = [
        'feature_0', 'feature_1', 'feature_2', 'feature_3', 'feature_4'
    ];
    const input = {};
    features.forEach(f => {
        input[f] = parseFloat(form[f].value);
    });
    const response = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify([input])
    });
    const result = await response.json();
    document.getElementById('prediction-result').textContent =
        result.predictions ? `Prediction: ${result.predictions[0]}` : `Error: ${result.error}`;
});

// EDA plot placeholder
window.onload = function() {
    document.getElementById('eda-plot').innerHTML =
        '<img src="https://via.placeholder.com/600x300?text=EDA+Plot" alt="EDA Plot" style="width:100%;border-radius:8px;">';
};
