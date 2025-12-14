// Cloudflare Worker Cron Job: Refresh Numbeo Data
// File: functions/scheduled/refresh-numbeo.js

export default {
  async scheduled(event, env, ctx) {
    console.log('Starting Numbeo data refresh...');
    
    // Polish cities to track (major cities from each voivodeship)
    const POLISH_CITIES = [
      { name: 'Warsaw', slug: 'Warsaw', voivodeship_id: 1 },
      { name: 'Krakow', slug: 'Krakow', voivodeship_id: 4 },
      { name: 'Lodz', slug: 'Lodz', voivodeship_id: 6 },
      { name: 'Wroclaw', slug: 'Wroclaw', voivodeship_id: 5 },
      { name: 'Poznan', slug: 'Poznan', voivodeship_id: 3 },
      { name: 'Gdansk', slug: 'Gdansk', voivodeship_id: 12 },
      { name: 'Szczecin', slug: 'Szczecin', voivodeship_id: 7 },
      { name: 'Bydgoszcz', slug: 'Bydgoszcz', voivodeship_id: 11 },
      { name: 'Lublin', slug: 'Lublin', voivodeship_id: 8 },
      { name: 'Katowice', slug: 'Katowice', voivodeship_id: 2 },
      { name: 'Bialystok', slug: 'Bialystok', voivodeship_id: 13 },
      { name: 'Czestochowa', slug: 'Czestochowa', voivodeship_id: 2 },
      { name: 'Radom', slug: 'Radom', voivodeship_id: 1 },
      { name: 'Torun', slug: 'Torun', voivodeship_id: 11 },
      { name: 'Rzeszow', slug: 'Rzeszow', voivodeship_id: 9 },
      { name: 'Kielce', slug: 'Kielce', voivodeship_id: 14 }
    ];

    const API_KEY = env.NUMBEO_API_KEY; // Set in Cloudflare environment variables
    
    if (!API_KEY) {
      console.error('NUMBEO_API_KEY not found in environment variables');
      return;
    }

    let successCount = 0;
    let errorCount = 0;

    // Process each city
    for (const city of POLISH_CITIES) {
      try {
        await processCityData(env, city, API_KEY);
        successCount++;
        
        // Rate limiting: wait 1 second between requests
        await new Promise(resolve => setTimeout(resolve, 1000));
      } catch (error) {
        console.error(`Error processing ${city.name}:`, error);
        errorCount++;
      }
    }

    // Update EU comparison data
    try {
      await updateEUComparisons(env, API_KEY);
      console.log('EU comparisons updated successfully');
    } catch (error) {
      console.error('Error updating EU comparisons:', error);
    }

    console.log(`Numbeo refresh completed. Success: ${successCount}, Errors: ${errorCount}`);
  }
};

async function processCityData(env, city, apiKey) {
  // Get cost of living data
  const costResponse = await fetch(
    `https://www.numbeo.com/api/city_prices?api_key=${apiKey}&query=${city.slug}, Poland`
  );
  
  if (!costResponse.ok) {
    throw new Error(`Numbeo API error for ${city.name}: ${costResponse.status}`);
  }

  const costData = await costResponse.json();
  
  // Get quality of life data
  const qualityResponse = await fetch(
    `https://www.numbeo.com/api/indices?api_key=${apiKey}&query=${city.slug}, Poland`
  );
  
  const qualityData = qualityResponse.ok ? await qualityResponse.json() : null;

  // Find city ID in database
  const cityQuery = `
    SELECT id FROM cities 
    WHERE name_en = ? OR name = ?
  `;
  const cityResult = await env.DB.prepare(cityQuery).bind(city.name, city.name).first();
  
  if (!cityResult) {
    console.warn(`City ${city.name} not found in database, skipping...`);
    return;
  }

  const cityId = cityResult.id;
  const today = new Date().toISOString().split('T')[0];

  // Parse cost of living data
  const costMetrics = parseCostLivingData(costData);
  
  // Insert/update cost of living data
  const costInsertQuery = `
    INSERT OR REPLACE INTO cost_living_data (
      city_id, data_date, cost_index, rent_index, groceries_index, 
      restaurant_index, local_purchasing_power_index,
      meal_inexpensive_restaurant, meal_for_2_midrange, domestic_beer,
      cappuccino, milk_1l, bread_loaf,
      apartment_1br_center, apartment_1br_outside, apartment_3br_center, apartment_3br_outside,
      oneway_ticket, monthly_pass, taxi_start, taxi_1km, gasoline_1l,
      utilities_basic, internet, mobile_plan,
      source, last_updated
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'numbeo', CURRENT_TIMESTAMP)
  `;

  await env.DB.prepare(costInsertQuery).bind(
    cityId, today,
    costMetrics.cost_index, costMetrics.rent_index, costMetrics.groceries_index,
    costMetrics.restaurant_index, costMetrics.local_purchasing_power_index,
    costMetrics.meal_inexpensive_restaurant, costMetrics.meal_for_2_midrange, costMetrics.domestic_beer,
    costMetrics.cappuccino, costMetrics.milk_1l, costMetrics.bread_loaf,
    costMetrics.apartment_1br_center, costMetrics.apartment_1br_outside, 
    costMetrics.apartment_3br_center, costMetrics.apartment_3br_outside,
    costMetrics.oneway_ticket, costMetrics.monthly_pass, costMetrics.taxi_start, 
    costMetrics.taxi_1km, costMetrics.gasoline_1l,
    costMetrics.utilities_basic, costMetrics.internet, costMetrics.mobile_plan
  ).run();

  // Insert quality metrics if available
  if (qualityData && qualityData.indices) {
    const qualityMetrics = parseQualityData(qualityData);
    
    const qualityInsertQuery = `
      INSERT OR REPLACE INTO quality_metrics (
        city_id, data_date, quality_of_life_index, purchasing_power_index,
        safety_index, health_care_index, cost_of_living_index, 
        property_price_to_income_ratio, traffic_commute_time_index,
        pollution_index, climate_index, source, last_updated
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'numbeo', CURRENT_TIMESTAMP)
    `;

    await env.DB.prepare(qualityInsertQuery).bind(
      cityId, today,
      qualityMetrics.quality_of_life_index, qualityMetrics.purchasing_power_index,
      qualityMetrics.safety_index, qualityMetrics.health_care_index, 
      qualityMetrics.cost_of_living_index, qualityMetrics.property_price_to_income_ratio,
      qualityMetrics.traffic_commute_time_index, qualityMetrics.pollution_index, 
      qualityMetrics.climate_index
    ).run();
  }

  console.log(`Successfully updated data for ${city.name}`);
}

function parseCostLivingData(data) {
  const metrics = {
    cost_index: null,
    rent_index: null,
    groceries_index: null,
    restaurant_index: null,
    local_purchasing_power_index: null,
    meal_inexpensive_restaurant: null,
    meal_for_2_midrange: null,
    domestic_beer: null,
    cappuccino: null,
    milk_1l: null,
    bread_loaf: null,
    apartment_1br_center: null,
    apartment_1br_outside: null,
    apartment_3br_center: null,
    apartment_3br_outside: null,
    oneway_ticket: null,
    monthly_pass: null,
    taxi_start: null,
    taxi_1km: null,
    gasoline_1l: null,
    utilities_basic: null,
    internet: null,
    mobile_plan: null
  };

  // Map Numbeo item IDs to our database fields
  const itemMapping = {
    1: 'meal_inexpensive_restaurant',
    2: 'meal_for_2_midrange',
    4: 'domestic_beer',
    114: 'cappuccino',
    13: 'milk_1l',
    9: 'bread_loaf',
    26: 'apartment_1br_center',
    27: 'apartment_1br_outside',
    28: 'apartment_3br_center',
    29: 'apartment_3br_outside',
    18: 'oneway_ticket',
    19: 'monthly_pass',
    105: 'taxi_start',
    106: 'taxi_1km',
    24: 'gasoline_1l',
    30: 'utilities_basic',
    33: 'internet',
    31: 'mobile_plan'
  };

  // Parse prices array
  if (data.prices) {
    data.prices.forEach(item => {
      const field = itemMapping[item.item_id];
      if (field && item.average_price) {
        metrics[field] = parseFloat(item.average_price);
      }
    });
  }

  // Parse indices if available
  if (data.cpi_index) metrics.cost_index = parseFloat(data.cpi_index);
  if (data.rent_index) metrics.rent_index = parseFloat(data.rent_index);
  if (data.groceries_index) metrics.groceries_index = parseFloat(data.groceries_index);
  if (data.restaurant_price_index) metrics.restaurant_index = parseFloat(data.restaurant_price_index);
  if (data.local_purchasing_power_index) metrics.local_purchasing_power_index = parseFloat(data.local_purchasing_power_index);

  return metrics;
}

function parseQualityData(data) {
  const indices = data.indices || {};
  
  return {
    quality_of_life_index: indices.quality_of_life_index ? parseFloat(indices.quality_of_life_index) : null,
    purchasing_power_index: indices.purchasing_power_index ? parseFloat(indices.purchasing_power_index) : null,
    safety_index: indices.safety_index ? parseFloat(indices.safety_index) : null,
    health_care_index: indices.health_care_index ? parseFloat(indices.health_care_index) : null,
    cost_of_living_index: indices.cost_of_living_index ? parseFloat(indices.cost_of_living_index) : null,
    property_price_to_income_ratio: indices.property_price_to_income_ratio ? parseFloat(indices.property_price_to_income_ratio) : null,
    traffic_commute_time_index: indices.traffic_commute_time_index ? parseFloat(indices.traffic_commute_time_index) : null,
    pollution_index: indices.pollution_index ? parseFloat(indices.pollution_index) : null,
    climate_index: indices.climate_index ? parseFloat(indices.climate_index) : null
  };
}

async function updateEUComparisons(env, apiKey) {
  // Get European capitals data for comparison
  const EU_CAPITALS = ['Berlin, Germany', 'Paris, France', 'Rome, Italy', 'Madrid, Spain', 
                      'Amsterdam, Netherlands', 'Vienna, Austria', 'Prague, Czech Republic'];
  
  const today = new Date().toISOString().split('T')[0];
  let euData = [];

  // Fetch data for EU capitals (with rate limiting)
  for (const city of EU_CAPITALS) {
    try {
      const response = await fetch(
        `https://www.numbeo.com/api/indices?api_key=${apiKey}&query=${city}`
      );
      
      if (response.ok) {
        const data = await response.json();
        if (data.indices) {
          euData.push(data.indices);
        }
      }
      
      await new Promise(resolve => setTimeout(resolve, 1000)); // Rate limiting
    } catch (error) {
      console.error(`Error fetching data for ${city}:`, error);
    }
  }

  if (euData.length === 0) return;

  // Calculate EU averages
  const indicators = ['cost_of_living_index', 'rent_index', 'purchasing_power_index', 'safety_index'];
  
  for (const indicator of indicators) {
    const values = euData.map(d => parseFloat(d[indicator])).filter(v => !isNaN(v));
    if (values.length === 0) continue;

    const euAverage = values.reduce((a, b) => a + b, 0) / values.length;
    const euMedian = values.sort((a, b) => a - b)[Math.floor(values.length / 2)];

    // Get Poland's value (average of major cities)
    const polandQuery = `
      SELECT AVG(${indicator === 'cost_of_living_index' ? 'cost_index' : 
                   indicator === 'rent_index' ? 'rent_index' :
                   indicator === 'purchasing_power_index' ? 'local_purchasing_power_index' : 
                   'safety_index'}) as poland_avg
      FROM v_latest_cost_living
      WHERE city_id IN (SELECT id FROM cities WHERE is_major = 1)
    `;

    const polandResult = await env.DB.prepare(polandQuery).first();
    if (!polandResult?.poland_avg) continue;

    const polandValue = parseFloat(polandResult.poland_avg);
    const polandRank = values.filter(v => v < polandValue).length + 1;
    const polandPercentile = (polandRank / (values.length + 1)) * 100;

    // Insert/update EU comparison
    const insertQuery = `
      INSERT OR REPLACE INTO eu_comparisons (
        indicator_type, indicator_subtype, poland_value, eu_average, eu_median,
        poland_rank, total_countries, poland_percentile, data_date, source
      ) VALUES ('cost_living', ?, ?, ?, ?, ?, ?, ?, ?, 'numbeo')
    `;

    await env.DB.prepare(insertQuery).bind(
      indicator, polandValue, euAverage, euMedian,
      polandRank, values.length + 1, polandPercentile, today
    ).run();
  }
}