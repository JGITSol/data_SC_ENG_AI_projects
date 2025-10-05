// tests/integration/test_poland_gdp.js
// Test integracyjny endpointu /api/poland-gdp

import fetch from 'node-fetch';
import assert from 'assert';


const BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:3002/api';

describe('World Bank GDP API integration', () => {
  it('should return valid GDP per capita for Poland', async () => {
    const res = await fetch(`${BASE_URL}/poland-gdp`);
    assert.strictEqual(res.status, 200);
    const data = await res.json();
    assert.strictEqual(data.country, 'Poland');
    assert.ok(data.year >= 2020);
    assert.ok(data.gdp_per_capita_usd > 10000);
  });
});
