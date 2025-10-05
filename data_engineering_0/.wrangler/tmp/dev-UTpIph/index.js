var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// src/index.ts
var LOCATIONS = [
  { name: "Bia\u0142ystok", slug: "bialystok", lat: 53.1325, lon: 23.1688 },
  { name: "Bydgoszcz", slug: "bydgoszcz", lat: 53.1235, lon: 18.0084 },
  { name: "Cz\u0119stochowa", slug: "czestochowa", lat: 50.7964, lon: 19.1201 },
  { name: "Gda\u0144sk", slug: "gdansk", lat: 54.352, lon: 18.6466 },
  { name: "Katowice", slug: "katowice", lat: 50.2649, lon: 19.0238 },
  { name: "Kielce", slug: "kielce", lat: 50.8661, lon: 20.6286 },
  { name: "Krak\xF3w", slug: "krakow", lat: 50.0647, lon: 19.945 },
  { name: "Lublin", slug: "lublin", lat: 51.2465, lon: 22.5684 },
  { name: "\u0141\xF3d\u017A", slug: "lodz", lat: 51.7592, lon: 19.456 },
  { name: "Pozna\u0144", slug: "poznan", lat: 52.4064, lon: 16.9252 },
  { name: "Radom", slug: "radom", lat: 51.4027, lon: 21.1471 },
  { name: "Rzesz\xF3w", slug: "rzeszow", lat: 50.0412, lon: 21.9991 },
  { name: "Szczecin", slug: "szczecin", lat: 53.4285, lon: 14.5528 },
  { name: "Toru\u0144", slug: "torun", lat: 53.0138, lon: 18.5984 },
  { name: "Warsaw", slug: "warsaw", lat: 52.2297, lon: 21.0122 },
  { name: "Wroc\u0142aw", slug: "wroclaw", lat: 51.1079, lon: 17.0385 }
];
var src_default = {
  async fetch(request, env, _ctx) {
    const url = new URL(request.url);
    const path = url.pathname;
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type"
    };
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }
    try {
      if (path.startsWith("/api/")) {
        return await handleApiRequest(path, url, env, corsHeaders);
      }
      if (path === "/health") {
        return await handleHealthCheck(env, corsHeaders);
      }
      if (path === "/ingest/run" && request.method === "POST") {
        return await handleManualIngestion(env, corsHeaders);
      }
      return new Response("Poland Weather Data Lake API", {
        headers: { ...corsHeaders, "Content-Type": "text/plain" }
      });
    } catch (error) {
      console.error("Worker error:", error);
      return new Response(JSON.stringify({ error: "Internal server error" }), {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      });
    }
  },
  async scheduled(_event, env, _ctx) {
    console.log("Starting scheduled weather data ingestion...");
    try {
      await ingestWeatherData(env);
      console.log("Scheduled ingestion completed successfully");
    } catch (error) {
      console.error("Scheduled ingestion failed:", error);
    }
  }
};
async function handleApiRequest(path, url, env, corsHeaders) {
  const segments = path.split("/").filter(Boolean);
  switch (segments[1]) {
    case "locations":
      return new Response(JSON.stringify({ locations: LOCATIONS }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      });
    case "current": {
      const citySlug = url.searchParams.get("city");
      if (!citySlug) {
        return new Response(
          JSON.stringify({ error: "City parameter required" }),
          {
            status: 400,
            headers: { ...corsHeaders, "Content-Type": "application/json" }
          }
        );
      }
      return await getCurrentWeather(env, citySlug, corsHeaders);
    }
    case "hourly": {
      const hourlyCity = url.searchParams.get("city");
      const limit = parseInt(url.searchParams.get("limit") || "24");
      if (!hourlyCity) {
        return new Response(
          JSON.stringify({ error: "City parameter required" }),
          {
            status: 400,
            headers: { ...corsHeaders, "Content-Type": "application/json" }
          }
        );
      }
      return await getHourlyWeather(env, hourlyCity, limit, corsHeaders);
    }
    case "daily": {
      const dailyCity = url.searchParams.get("city");
      const days = parseInt(url.searchParams.get("days") || "7");
      if (!dailyCity) {
        return new Response(
          JSON.stringify({ error: "City parameter required" }),
          {
            status: 400,
            headers: { ...corsHeaders, "Content-Type": "application/json" }
          }
        );
      }
      return await getDailyWeather(env, dailyCity, days, corsHeaders);
    }
    default:
      return new Response(JSON.stringify({ error: "API endpoint not found" }), {
        status: 404,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      });
  }
}
__name(handleApiRequest, "handleApiRequest");
async function handleHealthCheck(env, corsHeaders) {
  try {
    const lastIngestion = await env.KV_NS.get("last_ingestion_time");
    const lastIngestionDate = lastIngestion ? new Date(lastIngestion) : null;
    const status = {
      status: "healthy",
      timestamp: (/* @__PURE__ */ new Date()).toISOString(),
      last_ingestion: lastIngestionDate?.toISOString() || "never",
      locations_count: LOCATIONS.length,
      services: {
        database: "connected",
        storage: "connected",
        kv: "connected"
      }
    };
    return new Response(JSON.stringify(status), {
      headers: { ...corsHeaders, "Content-Type": "application/json" }
    });
  } catch (error) {
    return new Response(
      JSON.stringify({
        status: "unhealthy",
        error: error instanceof Error ? error.message : "Unknown error"
      }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      }
    );
  }
}
__name(handleHealthCheck, "handleHealthCheck");
async function handleManualIngestion(env, corsHeaders) {
  try {
    await ingestWeatherData(env);
    return new Response(
      JSON.stringify({
        success: true,
        message: "Manual ingestion completed",
        timestamp: (/* @__PURE__ */ new Date()).toISOString()
      }),
      {
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      }
    );
  }
}
__name(handleManualIngestion, "handleManualIngestion");
async function getCurrentWeather(env, citySlug, corsHeaders) {
  const location = LOCATIONS.find((loc) => loc.slug === citySlug);
  if (!location) {
    return new Response(JSON.stringify({ error: "City not found" }), {
      status: 404,
      headers: { ...corsHeaders, "Content-Type": "application/json" }
    });
  }
  try {
    const response = await fetch(
      `https://api.open-meteo.com/v1/forecast?latitude=${location.lat}&longitude=${location.lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation&timezone=Europe/Warsaw`
    );
    if (!response.ok) {
      throw new Error("Weather API error");
    }
    const data = await response.json();
    const current = data.current;
    if (!current) {
      throw new Error("No current weather data available");
    }
    const result = {
      name: location.name,
      slug: location.slug,
      timestamp: current.time,
      temp_c: Math.round(current.temperature_2m * 10) / 10,
      wind_mps: current.wind_speed_10m,
      humidity_pct: current.relative_humidity_2m,
      precip_mm: current.precipitation
    };
    return new Response(JSON.stringify(result), {
      headers: { ...corsHeaders, "Content-Type": "application/json" }
    });
  } catch (_error) {
    return new Response(
      JSON.stringify({ error: "Failed to fetch weather data" }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      }
    );
  }
}
__name(getCurrentWeather, "getCurrentWeather");
async function getHourlyWeather(env, citySlug, limit, corsHeaders) {
  const location = LOCATIONS.find((loc) => loc.slug === citySlug);
  if (!location) {
    return new Response(JSON.stringify({ error: "City not found" }), {
      status: 404,
      headers: { ...corsHeaders, "Content-Type": "application/json" }
    });
  }
  try {
    const response = await fetch(
      `https://api.open-meteo.com/v1/forecast?latitude=${location.lat}&longitude=${location.lon}&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation&timezone=Europe/Warsaw&forecast_days=1`
    );
    if (!response.ok) {
      throw new Error("Weather API error");
    }
    const data = await response.json();
    const hourly = data.hourly;
    if (!hourly) {
      throw new Error("No hourly weather data available");
    }
    const result = {
      data: hourly.time.slice(0, limit).map((time, index) => ({
        timestamp: time,
        temp_c: Math.round(hourly.temperature_2m[index] * 10) / 10,
        wind_mps: hourly.wind_speed_10m[index],
        humidity_pct: hourly.relative_humidity_2m[index],
        precip_mm: hourly.precipitation[index]
      })),
      count: Math.min(limit, hourly.time.length)
    };
    return new Response(JSON.stringify(result), {
      headers: { ...corsHeaders, "Content-Type": "application/json" }
    });
  } catch (_error) {
    return new Response(
      JSON.stringify({ error: "Failed to fetch hourly weather data" }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      }
    );
  }
}
__name(getHourlyWeather, "getHourlyWeather");
async function getDailyWeather(env, citySlug, days, corsHeaders) {
  const location = LOCATIONS.find((loc) => loc.slug === citySlug);
  if (!location) {
    return new Response(JSON.stringify({ error: "City not found" }), {
      status: 404,
      headers: { ...corsHeaders, "Content-Type": "application/json" }
    });
  }
  try {
    const response = await fetch(
      `https://api.open-meteo.com/v1/forecast?latitude=${location.lat}&longitude=${location.lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max&timezone=Europe/Warsaw&forecast_days=${days}`
    );
    if (!response.ok) {
      throw new Error("Weather API error");
    }
    const data = await response.json();
    const daily = data.daily;
    if (!daily) {
      throw new Error("No daily weather data available");
    }
    const result = {
      data: daily.time.map((time, index) => ({
        date: time,
        temp_min_c: Math.round(daily.temperature_2m_min[index] * 10) / 10,
        temp_max_c: Math.round(daily.temperature_2m_max[index] * 10) / 10,
        precip_mm: daily.precipitation_sum[index],
        wind_max_mps: daily.wind_speed_10m_max[index]
      })),
      count: daily.time.length
    };
    return new Response(JSON.stringify(result), {
      headers: { ...corsHeaders, "Content-Type": "application/json" }
    });
  } catch (_error) {
    return new Response(
      JSON.stringify({ error: "Failed to fetch daily weather data" }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      }
    );
  }
}
__name(getDailyWeather, "getDailyWeather");
async function ingestWeatherData(env) {
  console.log(
    "Starting weather data ingestion for",
    LOCATIONS.length,
    "cities"
  );
  for (const location of LOCATIONS) {
    try {
      console.log(`Ingesting data for ${location.name}...`);
      const response = await fetch(
        `https://api.open-meteo.com/v1/forecast?latitude=${location.lat}&longitude=${location.lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max&timezone=Europe/Warsaw&forecast_days=7`
      );
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      const weatherData = await response.json();
      const timestamp = (/* @__PURE__ */ new Date()).toISOString().replace(/[:.]/g, "-");
      const r2Key = `raw/${location.slug}/${timestamp.split("T")[0]}/${timestamp.split("T")[1].split(".")[0]}_open-meteo.json`;
      await env.R2_BUCKET.put(r2Key, JSON.stringify(weatherData), {
        customMetadata: {
          city: location.name,
          ingestion_time: (/* @__PURE__ */ new Date()).toISOString()
        }
      });
      console.log(`\u2713 Data stored for ${location.name} in R2: ${r2Key}`);
      await new Promise((resolve) => setTimeout(resolve, 1e3));
    } catch (error) {
      console.error(`\u2717 Failed to ingest data for ${location.name}:`, error);
    }
  }
  await env.KV_NS.put("last_ingestion_time", (/* @__PURE__ */ new Date()).toISOString());
  console.log("Weather data ingestion completed");
}
__name(ingestWeatherData, "ingestWeatherData");

// node_modules/wrangler/templates/middleware/middleware-ensure-req-body-drained.ts
var drainBody = /* @__PURE__ */ __name(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } finally {
    try {
      if (request.body !== null && !request.bodyUsed) {
        const reader = request.body.getReader();
        while (!(await reader.read()).done) {
        }
      }
    } catch (e) {
      console.error("Failed to drain the unused request body.", e);
    }
  }
}, "drainBody");
var middleware_ensure_req_body_drained_default = drainBody;

// node_modules/wrangler/templates/middleware/middleware-miniflare3-json-error.ts
function reduceError(e) {
  return {
    name: e?.name,
    message: e?.message ?? String(e),
    stack: e?.stack,
    cause: e?.cause === void 0 ? void 0 : reduceError(e.cause)
  };
}
__name(reduceError, "reduceError");
var jsonError = /* @__PURE__ */ __name(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } catch (e) {
    const error = reduceError(e);
    return Response.json(error, {
      status: 500,
      headers: { "MF-Experimental-Error-Stack": "true" }
    });
  }
}, "jsonError");
var middleware_miniflare3_json_error_default = jsonError;

// .wrangler/tmp/bundle-KJ4azo/middleware-insertion-facade.js
var __INTERNAL_WRANGLER_MIDDLEWARE__ = [
  middleware_ensure_req_body_drained_default,
  middleware_miniflare3_json_error_default
];
var middleware_insertion_facade_default = src_default;

// node_modules/wrangler/templates/middleware/common.ts
var __facade_middleware__ = [];
function __facade_register__(...args) {
  __facade_middleware__.push(...args.flat());
}
__name(__facade_register__, "__facade_register__");
function __facade_invokeChain__(request, env, ctx, dispatch, middlewareChain) {
  const [head, ...tail] = middlewareChain;
  const middlewareCtx = {
    dispatch,
    next(newRequest, newEnv) {
      return __facade_invokeChain__(newRequest, newEnv, ctx, dispatch, tail);
    }
  };
  return head(request, env, ctx, middlewareCtx);
}
__name(__facade_invokeChain__, "__facade_invokeChain__");
function __facade_invoke__(request, env, ctx, dispatch, finalMiddleware) {
  return __facade_invokeChain__(request, env, ctx, dispatch, [
    ...__facade_middleware__,
    finalMiddleware
  ]);
}
__name(__facade_invoke__, "__facade_invoke__");

// .wrangler/tmp/bundle-KJ4azo/middleware-loader.entry.ts
var __Facade_ScheduledController__ = class ___Facade_ScheduledController__ {
  constructor(scheduledTime, cron, noRetry) {
    this.scheduledTime = scheduledTime;
    this.cron = cron;
    this.#noRetry = noRetry;
  }
  static {
    __name(this, "__Facade_ScheduledController__");
  }
  #noRetry;
  noRetry() {
    if (!(this instanceof ___Facade_ScheduledController__)) {
      throw new TypeError("Illegal invocation");
    }
    this.#noRetry();
  }
};
function wrapExportedHandler(worker) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__ === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__.length === 0) {
    return worker;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__) {
    __facade_register__(middleware);
  }
  const fetchDispatcher = /* @__PURE__ */ __name(function(request, env, ctx) {
    if (worker.fetch === void 0) {
      throw new Error("Handler does not export a fetch() function.");
    }
    return worker.fetch(request, env, ctx);
  }, "fetchDispatcher");
  return {
    ...worker,
    fetch(request, env, ctx) {
      const dispatcher = /* @__PURE__ */ __name(function(type, init) {
        if (type === "scheduled" && worker.scheduled !== void 0) {
          const controller = new __Facade_ScheduledController__(
            Date.now(),
            init.cron ?? "",
            () => {
            }
          );
          return worker.scheduled(controller, env, ctx);
        }
      }, "dispatcher");
      return __facade_invoke__(request, env, ctx, dispatcher, fetchDispatcher);
    }
  };
}
__name(wrapExportedHandler, "wrapExportedHandler");
function wrapWorkerEntrypoint(klass) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__ === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__.length === 0) {
    return klass;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__) {
    __facade_register__(middleware);
  }
  return class extends klass {
    #fetchDispatcher = /* @__PURE__ */ __name((request, env, ctx) => {
      this.env = env;
      this.ctx = ctx;
      if (super.fetch === void 0) {
        throw new Error("Entrypoint class does not define a fetch() function.");
      }
      return super.fetch(request);
    }, "#fetchDispatcher");
    #dispatcher = /* @__PURE__ */ __name((type, init) => {
      if (type === "scheduled" && super.scheduled !== void 0) {
        const controller = new __Facade_ScheduledController__(
          Date.now(),
          init.cron ?? "",
          () => {
          }
        );
        return super.scheduled(controller);
      }
    }, "#dispatcher");
    fetch(request) {
      return __facade_invoke__(
        request,
        this.env,
        this.ctx,
        this.#dispatcher,
        this.#fetchDispatcher
      );
    }
  };
}
__name(wrapWorkerEntrypoint, "wrapWorkerEntrypoint");
var WRAPPED_ENTRY;
if (typeof middleware_insertion_facade_default === "object") {
  WRAPPED_ENTRY = wrapExportedHandler(middleware_insertion_facade_default);
} else if (typeof middleware_insertion_facade_default === "function") {
  WRAPPED_ENTRY = wrapWorkerEntrypoint(middleware_insertion_facade_default);
}
var middleware_loader_entry_default = WRAPPED_ENTRY;
export {
  __INTERNAL_WRANGLER_MIDDLEWARE__,
  middleware_loader_entry_default as default
};
//# sourceMappingURL=index.js.map
