/**
 * Automated Test Suite for Weather Prediction Engine
 */
import { predictNext24h, featureImportance } from './prediction_engine.js';

const mockHistory = [
    { temp: 10, hum: 50, press: 1010, wind: 10 },
    { temp: 11, hum: 52, press: 1011, wind: 11 },
    { temp: 12, hum: 54, press: 1012, wind: 12 },
    { temp: 13, hum: 56, press: 1013, wind: 13 },
    { temp: 14, hum: 58, press: 1014, wind: 14 },
    { temp: 15, hum: 60, press: 1015, wind: 15 },
    { temp: 16, hum: 62, press: 1016, wind: 16 }
];

function testPrediction() {
    console.log("Running: testPrediction...");
    const result = predictNext24h(mockHistory);

    if (typeof result.value === 'number') {
        console.log("✅ Prediction value is a number:", result.value);
    } else {
        throw new Error("❌ Prediction value is not a number");
    }

    if (result.confidence >= 0 && result.confidence <= 1) {
        console.log("✅ Confidence is within [0, 1]:", result.confidence);
    } else {
        throw new Error("❌ Confidence is out of bounds");
    }
}

function testFeatureImportance() {
    console.log("Running: testFeatureImportance...");
    const keys = ['tempTrend', 'pressureGradient', 'humidityLevel', 'windEffect'];
    let total = 0;

    keys.forEach(key => {
        if (typeof featureImportance[key] === 'number') {
            console.log(`✅ Feature importance for ${key} is a number: ${featureImportance[key]}`);
            total += featureImportance[key];
        } else {
            throw new Error(`❌ Feature importance for ${key} is missing or not a number`);
        }
    });

    if (Math.abs(total - 1.0) < 0.001) {
        console.log("✅ Total feature importance matches 100%");
    } else {
        console.log("⚠️ Total feature importance does not match 100%:", total);
    }
}

try {
    testPrediction();
    testFeatureImportance();
    console.log("\n✨ All tests passed successfully!");
} catch (error) {
    console.error("\n💥 Test suite failed:");
    console.error(error.message);
    process.exit(1);
}
