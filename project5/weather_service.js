/**
 * Weather Service for fetching real-time and historical weather data
 * from Open-Meteo (free API, no auth required).
 */

export const capitals = {
    "Warsaw": { lat: 52.2297, lon: 21.0122 },
    "Berlin": { lat: 52.5200, lon: 13.4050 },
    "Paris": { lat: 48.8566, lon: 2.3522 },
    "London": { lat: 51.5074, lon: -0.1278 },
    "Vienna": { lat: 48.2082, lon: 16.3738 },
    "Rome": { lat: 41.9028, lon: 12.4964 },
    "Madrid": { lat: 40.4168, lon: -3.7038 },
    "Amsterdam": { lat: 52.3676, lon: 4.9041 },
    "Prague": { lat: 50.0755, lon: 14.4378 },
    "Brussels": { lat: 50.8503, lon: 4.3517 }
};

/**
 * Fetches current weather and 7-day history for a given coordinate.
 * @param {number} lat 
 * @param {number} lon 
 * @returns {Promise<Object>}
 */
export async function fetchWeatherData(lat, lon) {
    const today = new Date();
    const endDate = today.toISOString().split('T')[0];
    const startDate = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];

    const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&hourly=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,precipitation,uv_index,apparent_temperature&past_days=7&forecast_days=1&timezone=auto`;

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Weather API error: ${response.statusText}`);
        const data = await response.json();

        // Process hourly data into daily summaries (taking mid-day or avg)
        // For simplicity in this lab, we'll take the value at 12:00 for each of the last 7 days
        const history = [];
        const hourly = data.hourly;

        // Open-Meteo returns past_days + forecast_days hourly data.
        // We want the last 7 days (index 0 to 167)
        for (let i = 0; i < 7; i++) {
            const index = i * 24 + 12; // 12:00 PM for each day
            history.push({
                date: hourly.time[index],
                temp: Math.round(hourly.temperature_2m[index]),
                hum: Math.round(hourly.relative_humidity_2m[index]),
                press: Math.round(hourly.surface_pressure[index]),
                wind: Math.round(hourly.wind_speed_10m[index]),
                precip: hourly.precipitation[index],
                uv: hourly.uv_index[index],
                appTemp: Math.round(hourly.apparent_temperature[index])
            });
        }

        // Current is the latest available in forecast (usually index around 168+ depending on when called)
        // But we can just use the last one in history or the very latest hourly
        const latestIdx = hourly.time.length - 1; // Most recent data point
        const current = {
            temp: Math.round(hourly.temperature_2m[latestIdx]),
            hum: Math.round(hourly.relative_humidity_2m[latestIdx]),
            press: Math.round(hourly.surface_pressure[latestIdx]),
            wind: Math.round(hourly.wind_speed_10m[latestIdx]),
            precip: hourly.precipitation[latestIdx],
            uv: hourly.uv_index[latestIdx],
            appTemp: Math.round(hourly.apparent_temperature[latestIdx])
        };

        return {
            location: [lat, lon],
            history: history,
            current: current
        };
    } catch (error) {
        console.error("Failed to fetch weather data:", error);
        throw error;
    }
}
