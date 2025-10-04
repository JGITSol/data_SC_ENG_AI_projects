// Cloudflare Pages Function: Cost of Living API
// File: functions/api/cost-living.js

export async function onRequestGet(context) {
  const { request, env, params } = context;
  const url = new URL(request.url);
  const path = url.pathname.split('/').pop();

  try {
    switch (path) {
      case 'cities':
        return await getCitiesCostLiving(env);
      case 'compare':
        return await compareCities(env, url.searchParams);
      case 'poland-vs-eu':
        return await getPolandVsEU(env);
      default:
        return new Response('Not Found', { status: 404 });
    }
  } catch (error) {
    console.error('Cost living API error:', error);
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

async function getCitiesCostLiving(env) {
  const query = `
    SELECT 
      c.id,
      c.name,
      c.name_en,
      c.population,
      v.name as voivodeship,
      v.name_en as voivodeship_en,
      cld.cost_index,
      cld.rent_index,
      cld.groceries_index,
      cld.restaurant_index,
      cld.local_purchasing_power_index,
      cld.data_date
    FROM v_latest_cost_living cld
    JOIN cities c ON cld.city_id = c.id
    JOIN voivodeships v ON c.voivodeship_id = v.id
    WHERE c.is_major = 1
    ORDER BY c.population DESC
  `;

  const result = await env.DB.prepare(query).all();
  
  return new Response(JSON.stringify({
    cities: result.results,
    last_updated: new Date().toISOString(),
    count: result.results.length
  }), {
    headers: { 
      'Content-Type': 'application/json',
      'Cache-Control': 'public, max-age=3600' // Cache for 1 hour
    }
  });
}

async function compareCities(env, searchParams) {
  const city1 = searchParams.get('city1');
  const city2 = searchParams.get('city2');
  
  if (!city1 || !city2) {
    return new Response(JSON.stringify({ 
      error: 'Both city1 and city2 parameters required' 
    }), { 
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  const query = `
    SELECT 
      c.id,
      c.name,
      c.name_en,
      v.name as voivodeship,
      cld.cost_index,
      cld.rent_index,
      cld.groceries_index,
      cld.restaurant_index,
      cld.local_purchasing_power_index,
      cld.meal_inexpensive_restaurant,
      cld.apartment_1br_center,
      cld.monthly_pass,
      cld.utilities_basic,
      cld.data_date
    FROM v_latest_cost_living cld
    JOIN cities c ON cld.city_id = c.id
    JOIN voivodeships v ON c.voivodeship_id = v.id
    WHERE c.name_en IN (?, ?) OR c.name IN (?, ?)
  `;

  const result = await env.DB.prepare(query).bind(city1, city2, city1, city2).all();
  
  if (result.results.length < 2) {
    return new Response(JSON.stringify({ 
      error: 'One or both cities not found in database' 
    }), { 
      status: 404,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  // Calculate percentage differences
  const [cityA, cityB] = result.results;
  const comparison = {
    cities: [cityA, cityB],
    differences: {
      cost_index: ((cityB.cost_index - cityA.cost_index) / cityA.cost_index * 100).toFixed(2),
      rent_index: ((cityB.rent_index - cityA.rent_index) / cityA.rent_index * 100).toFixed(2),
      groceries_index: ((cityB.groceries_index - cityA.groceries_index) / cityA.groceries_index * 100).toFixed(2),
      restaurant_index: ((cityB.restaurant_index - cityA.restaurant_index) / cityA.restaurant_index * 100).toFixed(2),
      purchasing_power_index: ((cityB.local_purchasing_power_index - cityA.local_purchasing_power_index) / cityA.local_purchasing_power_index * 100).toFixed(2)
    },
    summary: cityB.cost_index > cityA.cost_index 
      ? `${cityB.name_en} is ${((cityB.cost_index - cityA.cost_index) / cityA.cost_index * 100).toFixed(1)}% more expensive than ${cityA.name_en}`
      : `${cityB.name_en} is ${((cityA.cost_index - cityB.cost_index) / cityB.cost_index * 100).toFixed(1)}% cheaper than ${cityA.name_en}`
  };

  return new Response(JSON.stringify(comparison), {
    headers: { 
      'Content-Type': 'application/json',
      'Cache-Control': 'public, max-age=3600'
    }
  });
}

async function getPolandVsEU(env) {
  const query = `
    SELECT 
      ec.indicator_subtype,
      ec.poland_value,
      ec.eu_average,
      ec.eu_median,
      ec.poland_rank,
      ec.total_countries,
      ec.poland_percentile,
      ec.data_date
    FROM eu_comparisons ec
    WHERE ec.indicator_type = 'cost_living'
    AND ec.data_date = (
      SELECT MAX(data_date) 
      FROM eu_comparisons 
      WHERE indicator_type = 'cost_living'
    )
    ORDER BY ec.indicator_subtype
  `;

  const result = await env.DB.prepare(query).all();
  
  // Also get major Polish cities average
  const polishCitiesQuery = `
    SELECT 
      AVG(cost_index) as avg_cost_index,
      AVG(rent_index) as avg_rent_index,
      AVG(groceries_index) as avg_groceries_index,
      AVG(local_purchasing_power_index) as avg_purchasing_power,
      COUNT(*) as cities_count
    FROM v_latest_cost_living
    WHERE city_id IN (SELECT id FROM cities WHERE is_major = 1)
  `;

  const polishAvg = await env.DB.prepare(polishCitiesQuery).first();

  return new Response(JSON.stringify({
    eu_comparisons: result.results,
    polish_cities_average: polishAvg,
    insights: generateCostLivingInsights(result.results, polishAvg),
    last_updated: new Date().toISOString()
  }), {
    headers: { 
      'Content-Type': 'application/json',
      'Cache-Control': 'public, max-age=7200' // Cache for 2 hours
    }
  });
}

function generateCostLivingInsights(euData, polishAvg) {
  const insights = [];
  
  // Find cost of living comparison
  const costComparison = euData.find(item => item.indicator_subtype === 'cost_index');
  if (costComparison) {
    if (costComparison.poland_percentile < 50) {
      insights.push(`Poland ranks in the bottom ${Math.round(costComparison.poland_percentile)}% for cost of living in the EU, making it relatively affordable.`);
    } else {
      insights.push(`Poland's cost of living is above the EU median, ranking ${costComparison.poland_rank} out of ${costComparison.total_countries} countries.`);
    }
  }

  // Find purchasing power comparison
  const purchasingPower = euData.find(item => item.indicator_subtype === 'purchasing_power_index');
  if (purchasingPower) {
    if (purchasingPower.poland_value < purchasingPower.eu_average) {
      insights.push(`Polish purchasing power is ${Math.round(((purchasingPower.eu_average - purchasingPower.poland_value) / purchasingPower.eu_average) * 100)}% below the EU average.`);
    }
  }

  // Warsaw vs major EU capitals insight
  if (polishAvg && polishAvg.avg_cost_index) {
    if (polishAvg.avg_cost_index < 60) {
      insights.push(`Major Polish cities are significantly more affordable than Western European capitals, with costs averaging ${Math.round(polishAvg.avg_cost_index)}% of New York levels.`);
    }
  }

  return insights;
}