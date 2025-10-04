// Poland Weather Dashboard JavaScript

class WeatherDashboard {
  constructor() {
    this.apiBase = this.getApiBase();
    this.currentCity = '';
    this.init();
  }

  getApiBase() {
    // Try to detect if we're running locally or in production
    if (
      location.hostname === 'localhost' ||
      location.hostname.includes('127.0.0.1')
    ) {
      return 'http://localhost:8787'; // Wrangler dev default
    }
    // In production, API should be on same domain or configure CORS
    return ''; // Same origin
  }

  async init() {
    await this.loadCities();
    this.setupEventListeners();
    await this.loadSystemStatus();
  }

  setupEventListeners() {
    // City selector
    document.getElementById('city-select').addEventListener('change', e => {
      this.currentCity = e.target.value;
      if (this.currentCity) {
        this.loadWeatherData();
      }
    });

    // Tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', e => {
        const tabName = e.target.dataset.tab;
        this.switchTab(tabName);

        if (
          this.currentCity &&
          (tabName === 'current' || tabName === 'hourly' || tabName === 'daily')
        ) {
          this.loadWeatherData();
        }
      });
    });
  }

  async loadCities() {
    try {
      const response = await fetch(`${this.apiBase}/api/locations`);
      const data = await response.json();

      const select = document.getElementById('city-select');
      select.innerHTML = '<option value="">Select a city...</option>';

      data.data.forEach(city => {
        const option = document.createElement('option');
        option.value = city.slug;
        option.textContent = city.name;
        select.appendChild(option);
      });
    } catch (error) {
      console.error('Failed to load cities:', error);
      document.getElementById('city-select').innerHTML =
        '<option value="">Error loading cities</option>';
    }
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
    const loading = document.getElementById('current-loading');
    const data = document.getElementById('current-data');

    loading.style.display = 'block';
    data.style.display = 'none';

    try {
      const response = await fetch(
        `${this.apiBase}/api/current?city=${this.currentCity}`
      );
      const weather = await response.json();

      if (response.ok) {
        document.getElementById('current-temp').textContent = Math.round(
          weather.temp_c || 0
        );
        document.getElementById('current-humidity').textContent =
          `${Math.round(weather.humidity_pct || 0)}%`;
        document.getElementById('current-wind').textContent =
          `${(weather.wind_mps || 0).toFixed(1)} m/s`;
        document.getElementById('current-precip').textContent =
          `${(weather.precip_mm || 0).toFixed(1)} mm`;
        document.getElementById('current-timestamp').textContent = new Date(
          weather.timestamp
        ).toLocaleString();

        loading.style.display = 'none';
        data.style.display = 'block';
      } else {
        loading.textContent = weather.error || 'No data available';
      }
    } catch (error) {
      console.error('Failed to load current weather:', error);
      loading.textContent = 'Failed to load data';
    }
  }

  async loadHourlyWeather() {
    const loading = document.getElementById('hourly-loading');
    const data = document.getElementById('hourly-data');

    loading.style.display = 'block';
    data.style.display = 'none';

    try {
      const response = await fetch(
        `${this.apiBase}/api/hourly?city=${this.currentCity}&limit=24`
      );
      const result = await response.json();

      if (response.ok && result.data) {
        const tbody = document.querySelector('#hourly-table tbody');
        tbody.innerHTML = '';

        result.data.forEach(row => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
                        <td>${new Date(row.timestamp).toLocaleString()}</td>
                        <td>${row.temp_c ? Math.round(row.temp_c) : '--'}</td>
                        <td>${row.humidity_pct ? Math.round(row.humidity_pct) : '--'}</td>
                        <td>${row.wind_mps ? row.wind_mps.toFixed(1) : '--'}</td>
                        <td>${row.precip_mm ? row.precip_mm.toFixed(1) : '0.0'}</td>
                    `;
          tbody.appendChild(tr);
        });

        loading.style.display = 'none';
        data.style.display = 'block';
      } else {
        loading.textContent = result.error || 'No hourly data available';
      }
    } catch (error) {
      console.error('Failed to load hourly weather:', error);
      loading.textContent = 'Failed to load data';
    }
  }

  async loadDailyWeather() {
    const loading = document.getElementById('daily-loading');
    const data = document.getElementById('daily-data');

    loading.style.display = 'block';
    data.style.display = 'none';

    try {
      const response = await fetch(
        `${this.apiBase}/api/daily?city=${this.currentCity}&days=7`
      );
      const result = await response.json();

      if (response.ok && result.data) {
        const tbody = document.querySelector('#daily-table tbody');
        tbody.innerHTML = '';

        result.data.forEach(row => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
                        <td>${new Date(row.date).toLocaleDateString()}</td>
                        <td>${row.temp_min_c ? Math.round(row.temp_min_c) : '--'}</td>
                        <td>${row.temp_max_c ? Math.round(row.temp_max_c) : '--'}</td>
                        <td>${row.precip_mm ? row.precip_mm.toFixed(1) : '0.0'}</td>
                        <td>${row.wind_max_mps ? row.wind_max_mps.toFixed(1) : '--'}</td>
                    `;
          tbody.appendChild(tr);
        });

        loading.style.display = 'none';
        data.style.display = 'block';
      } else {
        loading.textContent = result.error || 'No daily data available';
      }
    } catch (error) {
      console.error('Failed to load daily weather:', error);
      loading.textContent = 'Failed to load data';
    }
  }

  async loadSystemStatus() {
    try {
      const response = await fetch(`${this.apiBase}/health`);
      const status = await response.json();

      const lastIngestElement = document.getElementById('last-ingest');
      if (status.lastIngest && status.lastIngest !== 'never') {
        const date = new Date(status.lastIngest);
        const now = new Date();
        const diffMinutes = Math.floor((now - date) / (1000 * 60));

        if (diffMinutes < 60) {
          lastIngestElement.textContent = `${diffMinutes} minutes ago`;
          lastIngestElement.className = 'status-good';
        } else if (diffMinutes < 120) {
          lastIngestElement.textContent = `${Math.floor(diffMinutes / 60)} hour ago`;
          lastIngestElement.className = 'status-warning';
        } else {
          lastIngestElement.textContent = `${Math.floor(diffMinutes / 60)} hours ago`;
          lastIngestElement.className = 'status-error';
        }
      } else {
        lastIngestElement.textContent = 'Never';
        lastIngestElement.className = 'status-error';
      }
    } catch (error) {
      console.error('Failed to load system status:', error);
      document.getElementById('last-ingest').textContent = 'Unknown';
    }
  }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
  new WeatherDashboard();
});
