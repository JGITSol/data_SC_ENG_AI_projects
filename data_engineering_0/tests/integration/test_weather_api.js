// tests/integration/test_weather_api.js
// Test integracyjny endpointu /api/current dla Open-Meteo

import fetch from 'node-fetch';
import assert from 'assert';


const BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:3003/api';
const TEST_CITY = 'warsaw';

describe('Open-Meteo Weather API integration', () => {
  it('should return valid current weather for Warsaw', async () => {
    const res = await fetch(`${BASE_URL}/current?city=${TEST_CITY}`);
    assert.strictEqual(res.status, 200);
    const data = await res.json();
    assert.strictEqual(data.name, 'Warsaw');
    assert.ok(typeof data.temp_c === 'number');
    assert.ok(typeof data.wind_mps === 'number');
    assert.ok(typeof data.humidity_pct === 'number');
  });
});
