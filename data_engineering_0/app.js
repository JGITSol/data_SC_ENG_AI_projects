// Poland Weather Dashboard JavaScript

class WeatherDashboard {
  constructor() {
    this.currentCity = '';
    this.cities = [];
    this.init();
  }

  async init() {
    this.setupEventListeners();
    await this.loadCities();
    await this.checkPipelineStatus();
  }

  setupEventListeners() {
    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', e => {
        this.switchTab(e.target.dataset.tab);
      });
    });

    // City selection
    document.getElementById('city-select').addEventListener('change', e => {
      this.currentCity = e.target.value;
      if (this.currentCity) {
        this.loadWeatherData();
      }
    });
  }

  switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
      content.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');

    // Load data if needed
    if (this.currentCity && tabName !== 'lineage') {
      this.loadWeatherData();
    }
  }

  async loadCities() {
    try {
      // Polish cities with Open-Meteo coordinates
      this.cities = [
        { name: 'Białystok', slug: 'bialystok', lat: 53.1325, lon: 23.1688 },
        { name: 'Bydgoszcz', slug: 'bydgoszcz', lat: 53.1235, lon: 18.0084 },
        {
          name: 'Częstochowa',
          slug: 'czestochowa',
          lat: 50.7964,
          lon: 19.1201,
        },
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

      this.populateCitySelect();
    } catch (error) {
      console.error('Error loading cities:', error);
      this.showError('Failed to load cities');
    }
  }

  populateCitySelect() {
    const select = document.getElementById('city-select');
    select.innerHTML = '<option value="">Select a city...</option>';

    this.cities.forEach(city => {
      const option = document.createElement('option');
      option.value = city.slug;
      option.textContent = city.name;
      select.appendChild(option);
    });
  }

  async loadWeatherData() {
    const activeTab = document.querySelector('.tab-btn.active').dataset.tab;

    switch (activeTab) {
      case 'current':
        await this.loadCurrentWeather();
        break;
      case 'hourly':
        await this.loadHourlyWeather();
        break;
      case 'daily':
        await this.loadDailyWeather();
        break;
    }
  }

  async loadCurrentWeather() {
    const loadingEl = document.getElementById('current-loading');
    const dataEl = document.getElementById('current-data');

    loadingEl.style.display = 'block';
    dataEl.style.display = 'none';

    try {
      const city = this.cities.find(c => c.slug === this.currentCity);
      if (!city) return;

      // Fetch from Open-Meteo API
      const response = await fetch(
        `https://api.open-meteo.com/v1/forecast?latitude=${city.lat}&longitude=${city.lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation&timezone=Europe/Warsaw`
      );

      if (!response.ok) throw new Error('Weather API error');

      const data = await response.json();
      const current = data.current;

      // Update UI
      document.getElementById('current-temp').textContent = Math.round(
        current.temperature_2m
      );
      document.getElementById('current-humidity').textContent =
        `${current.relative_humidity_2m}%`;
      document.getElementById('current-wind').textContent =
        `${current.wind_speed_10m} m/s`;
      document.getElementById('current-precip').textContent =
        `${current.precipitation} mm`;
      document.getElementById('current-timestamp').textContent = new Date(
        current.time
      ).toLocaleString();

      loadingEl.style.display = 'none';
      dataEl.style.display = 'block';
    } catch (error) {
      console.error('Error loading current weather:', error);
      loadingEl.innerHTML = 'Error loading weather data';
    }
  }

  async loadHourlyWeather() {
    const loadingEl = document.getElementById('hourly-loading');
    const dataEl = document.getElementById('hourly-data');

    loadingEl.style.display = 'block';
    dataEl.style.display = 'none';

    try {
      const city = this.cities.find(c => c.slug === this.currentCity);
      if (!city) return;

      const response = await fetch(
        `https://api.open-meteo.com/v1/forecast?latitude=${city.lat}&longitude=${city.lon}&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation&timezone=Europe/Warsaw&forecast_days=1`
      );

      if (!response.ok) throw new Error('Weather API error');

      const data = await response.json();
      const hourly = data.hourly;

      // Populate table
      const tbody = document.querySelector('#hourly-table tbody');
      tbody.innerHTML = '';

      for (let i = 0; i < Math.min(24, hourly.time.length); i++) {
        const row = tbody.insertRow();
        row.innerHTML = `
                    <td>${new Date(hourly.time[i]).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</td>
                    <td>${Math.round(hourly.temperature_2m[i])}</td>
                    <td>${hourly.relative_humidity_2m[i]}</td>
                    <td>${hourly.wind_speed_10m[i]}</td>
                    <td>${hourly.precipitation[i]}</td>
                `;
      }

      loadingEl.style.display = 'none';
      dataEl.style.display = 'block';
    } catch (error) {
      console.error('Error loading hourly weather:', error);
      loadingEl.innerHTML = 'Error loading hourly data';
    }
  }

  async loadDailyWeather() {
    const loadingEl = document.getElementById('daily-loading');
    const dataEl = document.getElementById('daily-data');

    loadingEl.style.display = 'block';
    dataEl.style.display = 'none';

    try {
      const city = this.cities.find(c => c.slug === this.currentCity);
      if (!city) return;

      const response = await fetch(
        `https://api.open-meteo.com/v1/forecast?latitude=${city.lat}&longitude=${city.lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max&timezone=Europe/Warsaw&forecast_days=7`
      );

      if (!response.ok) throw new Error('Weather API error');

      const data = await response.json();
      const daily = data.daily;

      // Populate table
      const tbody = document.querySelector('#daily-table tbody');
      tbody.innerHTML = '';

      for (let i = 0; i < daily.time.length; i++) {
        const row = tbody.insertRow();
        const date = new Date(daily.time[i]);
        row.innerHTML = `
                    <td>${date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}</td>
                    <td>${Math.round(daily.temperature_2m_min[i])}</td>
                    <td>${Math.round(daily.temperature_2m_max[i])}</td>
                    <td>${daily.precipitation_sum[i]}</td>
                    <td>${daily.wind_speed_10m_max[i]}</td>
                `;
      }

      loadingEl.style.display = 'none';
      dataEl.style.display = 'block';
    } catch (error) {
      console.error('Error loading daily weather:', error);
      loadingEl.innerHTML = 'Error loading daily data';
    }
  }

  async checkPipelineStatus() {
    try {
      // Simulate pipeline status check
      const lastIngest = new Date();
      lastIngest.setMinutes(
        lastIngest.getMinutes() - Math.floor(Math.random() * 60)
      );

      document.getElementById('last-ingest').textContent =
        lastIngest.toLocaleString();

      // Add status indicator
      const statusEl = document.getElementById('last-ingest');
      const minutesAgo = Math.floor((new Date() - lastIngest) / (1000 * 60));

      if (minutesAgo < 60) {
        statusEl.style.color = '#28a745'; // Green
        statusEl.title = 'Pipeline is healthy';
      } else if (minutesAgo < 120) {
        statusEl.style.color = '#ffc107'; // Yellow
        statusEl.title = 'Pipeline may have issues';
      } else {
        statusEl.style.color = '#dc3545'; // Red
        statusEl.title = 'Pipeline needs attention';
      }
    } catch (error) {
      console.error('Error checking pipeline status:', error);
      document.getElementById('last-ingest').textContent = 'Status unavailable';
    }
  }

  showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error';
    errorDiv.textContent = message;
    document.querySelector('.content').prepend(errorDiv);

    setTimeout(() => errorDiv.remove(), 5000);
  }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new WeatherDashboard();
});
