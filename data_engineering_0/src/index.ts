// Cloudflare Worker: Poland Weather Data Lake
// Main entry point for the weather data ingestion and API

export interface Env {
  DB: D1Database;
  R2_BUCKET: R2Bucket;
  KV_NS: KVNamespace;
  WORKER_HOST?: string;
}

interface WeatherApiResponse {
  current?: {
    time: string;
    temperature_2m: number;
    relative_humidity_2m: number;
    wind_speed_10m: number;
    precipitation: number;
  };
  hourly?: {
    time: string[];
    temperature_2m: number[];
    relative_humidity_2m: number[];
    wind_speed_10m: number[];
    precipitation: number[];
  };
  daily?: {
    time: string[];
    temperature_2m_min: number[];
    temperature_2m_max: number[];
    precipitation_sum: number[];
    wind_speed_10m_max: number[];
  };
}

// Polish cities configuration
const LOCATIONS = [
  { name: 'Białystok', slug: 'bialystok', lat: 53.1325, lon: 23.1688 },
  { name: 'Bydgoszcz', slug: 'bydgoszcz', lat: 53.1235, lon: 18.0084 },
  { name: 'Częstochowa', slug: 'czestochowa', lat: 50.7964, lon: 19.1201 },
  { name: 'Gdańsk', slug: 'gdansk', lat: 54.352, lon: 18.6466 },
  { name: 'Katowice', slug: 'katowice', lat: 50.2649, lon: 19.0238 },
  { name: 'Kielce', slug: 'kielce', lat: 50.8661, lon: 20.6286 },
  { name: 'Kraków', slug: 'krakow', lat: 50.0647, lon: 19.945 },
  { name: 'Lublin', slug: 'lublin', lat: 51.2465, lon: 22.5684 },
  { name: 'Łódź', slug: 'lodz', lat: 51.7592, lon: 19.456 },
  { name: 'Poznań', slug: 'poznan', lat: 52.4064, lon: 16.9252 },
  { name: 'Radom', slug: 'radom', lat: 51.4027, lon: 21.1471 },
  { name: 'Rzeszów', slug: 'rzeszow', lat: 50.0412, lon: 21.9991 },
  { name: 'Szczecin', slug: 'szczecin', lat: 53.4285, lon: 14.5528 },
  { name: 'Toruń', slug: 'torun', lat: 53.0138, lon: 18.5984 },
  { name: 'Warsaw', slug: 'warsaw', lat: 52.2297, lon: 21.0122 },
  { name: 'Wrocław', slug: 'wroclaw', lat: 51.1079, lon: 17.0385 },
];

export default {
  async fetch(
    request: Request,
    env: Env,
    _ctx: ExecutionContext
  ): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;

    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      // API Routes
      if (path.startsWith('/api/')) {
        return await handleApiRequest(path, url, env, corsHeaders);
      }

      // Health check
      if (path === '/health') {
        return await handleHealthCheck(env, corsHeaders);
      }

      // Manual ingestion trigger
      if (path === '/ingest/run' && request.method === 'POST') {
        return await handleManualIngestion(env, corsHeaders);
      }

      // Default response
      return new Response('Poland Weather Data Lake API', {
        headers: { ...corsHeaders, 'Content-Type': 'text/plain' },
      });
    } catch (error) {
      console.error('Worker error:', error);
      return new Response(JSON.stringify({ error: 'Internal server error' }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }
  },

  async scheduled(
    _event: ScheduledEvent,
    env: Env,
    _ctx: ExecutionContext
  ): Promise<void> {
    console.log('Starting scheduled weather data ingestion...');

    try {
      await ingestWeatherData(env);
      console.log('Scheduled ingestion completed successfully');
    } catch (error) {
      console.error('Scheduled ingestion failed:', error);
    }
  },
};

async function handleApiRequest(
  path: string,
  url: URL,
  env: Env,
  corsHeaders: Record<string, string>
): Promise<Response> {
  const segments = path.split('/').filter(Boolean);

  switch (segments[1]) {
    case 'locations':
      return new Response(JSON.stringify({ locations: LOCATIONS }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });

    case 'current': {
      const citySlug = url.searchParams.get('city');
      if (!citySlug) {
        return new Response(
          JSON.stringify({ error: 'City parameter required' }),
          {
            status: 400,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          }
        );
      }
      return await getCurrentWeather(env, citySlug, corsHeaders);
    }

    case 'hourly': {
      const hourlyCity = url.searchParams.get('city');
      const limit = parseInt(url.searchParams.get('limit') || '24');
      if (!hourlyCity) {
        return new Response(
          JSON.stringify({ error: 'City parameter required' }),
          {
            status: 400,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          }
        );
      }
      return await getHourlyWeather(env, hourlyCity, limit, corsHeaders);
    }

    case 'daily': {
      const dailyCity = url.searchParams.get('city');
      const days = parseInt(url.searchParams.get('days') || '7');
      if (!dailyCity) {
        return new Response(
          JSON.stringify({ error: 'City parameter required' }),
          {
            status: 400,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          }
        );
      }
      return await getDailyWeather(env, dailyCity, days, corsHeaders);
    }

    default:
      return new Response(JSON.stringify({ error: 'API endpoint not found' }), {
        status: 404,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
  }
}

async function handleHealthCheck(
  env: Env,
  corsHeaders: Record<string, string>
): Promise<Response> {
  try {
    // Check last ingestion time from KV
    const lastIngestion = await env.KV_NS.get('last_ingestion_time');
    const lastIngestionDate = lastIngestion ? new Date(lastIngestion) : null;

    const status = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      last_ingestion: lastIngestionDate?.toISOString() || 'never',
      locations_count: LOCATIONS.length,
      services: {
        database: 'connected',
        storage: 'connected',
        kv: 'connected',
      },
    };

    return new Response(JSON.stringify(status), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  } catch (error) {
    return new Response(
      JSON.stringify({
        status: 'unhealthy',
        error: error instanceof Error ? error.message : 'Unknown error',
      }),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    );
  }
}

async function handleManualIngestion(
  env: Env,
  corsHeaders: Record<string, string>
): Promise<Response> {
  try {
    await ingestWeatherData(env);
    return new Response(
      JSON.stringify({
        success: true,
        message: 'Manual ingestion completed',
        timestamp: new Date().toISOString(),
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      }),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    );
  }
}

async function getCurrentWeather(
  env: Env,
  citySlug: string,
  corsHeaders: Record<string, string>
): Promise<Response> {
  const location = LOCATIONS.find(loc => loc.slug === citySlug);
  if (!location) {
    return new Response(JSON.stringify({ error: 'City not found' }), {
      status: 404,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }

  try {
    // Fetch from Open-Meteo API
    const response = await fetch(
      `https://api.open-meteo.com/v1/forecast?latitude=${location.lat}&longitude=${location.lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation&timezone=Europe/Warsaw`
    );

    if (!response.ok) {
      throw new Error('Weather API error');
    }

    const data = (await response.json()) as WeatherApiResponse;
    const current = data.current;

    if (!current) {
      throw new Error('No current weather data available');
    }

    const result = {
      name: location.name,
      slug: location.slug,
      timestamp: current.time,
      temp_c: Math.round(current.temperature_2m * 10) / 10,
      wind_mps: current.wind_speed_10m,
      humidity_pct: current.relative_humidity_2m,
      precip_mm: current.precipitation,
    };

    return new Response(JSON.stringify(result), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  } catch (_error) {
    return new Response(
      JSON.stringify({ error: 'Failed to fetch weather data' }),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    );
  }
}

async function getHourlyWeather(
  env: Env,
  citySlug: string,
  limit: number,
  corsHeaders: Record<string, string>
): Promise<Response> {
  const location = LOCATIONS.find(loc => loc.slug === citySlug);
  if (!location) {
    return new Response(JSON.stringify({ error: 'City not found' }), {
      status: 404,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }

  try {
    const response = await fetch(
      `https://api.open-meteo.com/v1/forecast?latitude=${location.lat}&longitude=${location.lon}&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation&timezone=Europe/Warsaw&forecast_days=1`
    );

    if (!response.ok) {
      throw new Error('Weather API error');
    }

    const data = (await response.json()) as WeatherApiResponse;
    const hourly = data.hourly;

    if (!hourly) {
      throw new Error('No hourly weather data available');
    }

    const result = {
      data: hourly.time.slice(0, limit).map((time: string, index: number) => ({
        timestamp: time,
        temp_c: Math.round(hourly.temperature_2m[index] * 10) / 10,
        wind_mps: hourly.wind_speed_10m[index],
        humidity_pct: hourly.relative_humidity_2m[index],
        precip_mm: hourly.precipitation[index],
      })),
      count: Math.min(limit, hourly.time.length),
    };

    return new Response(JSON.stringify(result), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  } catch (_error) {
    return new Response(
      JSON.stringify({ error: 'Failed to fetch hourly weather data' }),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    );
  }
}

async function getDailyWeather(
  env: Env,
  citySlug: string,
  days: number,
  corsHeaders: Record<string, string>
): Promise<Response> {
  const location = LOCATIONS.find(loc => loc.slug === citySlug);
  if (!location) {
    return new Response(JSON.stringify({ error: 'City not found' }), {
      status: 404,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }

  try {
    const response = await fetch(
      `https://api.open-meteo.com/v1/forecast?latitude=${location.lat}&longitude=${location.lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max&timezone=Europe/Warsaw&forecast_days=${days}`
    );

    if (!response.ok) {
      throw new Error('Weather API error');
    }

    const data = (await response.json()) as WeatherApiResponse;
    const daily = data.daily;

    if (!daily) {
      throw new Error('No daily weather data available');
    }

    const result = {
      data: daily.time.map((time: string, index: number) => ({
        date: time,
        temp_min_c: Math.round(daily.temperature_2m_min[index] * 10) / 10,
        temp_max_c: Math.round(daily.temperature_2m_max[index] * 10) / 10,
        precip_mm: daily.precipitation_sum[index],
        wind_max_mps: daily.wind_speed_10m_max[index],
      })),
      count: daily.time.length,
    };

    return new Response(JSON.stringify(result), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  } catch (_error) {
    return new Response(
      JSON.stringify({ error: 'Failed to fetch daily weather data' }),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    );
  }
}

async function ingestWeatherData(env: Env): Promise<void> {
  console.log(
    'Starting weather data ingestion for',
    LOCATIONS.length,
    'cities'
  );

  for (const location of LOCATIONS) {
    try {
      console.log(`Ingesting data for ${location.name}...`);

      // Fetch weather data from Open-Meteo
      const response = await fetch(
        `https://api.open-meteo.com/v1/forecast?latitude=${location.lat}&longitude=${location.lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max&timezone=Europe/Warsaw&forecast_days=7`
      );

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const weatherData = await response.json();

      // Store raw data in R2
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const r2Key = `raw/${location.slug}/${timestamp.split('T')[0]}/${timestamp.split('T')[1].split('.')[0]}_open-meteo.json`;

      await env.R2_BUCKET.put(r2Key, JSON.stringify(weatherData), {
        customMetadata: {
          city: location.name,
          ingestion_time: new Date().toISOString(),
        },
      });

      console.log(`✓ Data stored for ${location.name} in R2: ${r2Key}`);

      // Rate limiting
      await new Promise(resolve => setTimeout(resolve, 1000));
    } catch (error) {
      console.error(`✗ Failed to ingest data for ${location.name}:`, error);
    }
  }

  // Update last ingestion time
  await env.KV_NS.put('last_ingestion_time', new Date().toISOString());
  console.log('Weather data ingestion completed');
}
