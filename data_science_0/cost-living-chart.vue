<!-- Vue.js Component: Cost of Living Chart -->
<!-- File: frontend/src/components/CostLivingChart.vue -->

<template>
  <div class="cost-living-chart">
    <div class="chart-header">
      <h3>{{ title }}</h3>
      <div class="chart-controls">
        <select v-model="selectedMetric" @change="updateChart">
          <option value="cost_index">Overall Cost of Living</option>
          <option value="rent_index">Rent Index</option>
          <option value="groceries_index">Groceries Index</option>
          <option value="restaurant_index">Restaurant Index</option>
          <option value="local_purchasing_power_index">Purchasing Power</option>
        </select>
        <button 
          @click="compareWithEU" 
          :class="{ active: showEUComparison }"
          class="eu-toggle"
        >
          {{ showEUComparison ? 'Hide' : 'Show' }} EU Average
        </button>
      </div>
    </div>

    <div class="chart-container" ref="chartContainer">
      <canvas ref="chartCanvas"></canvas>
    </div>

    <div class="chart-insights" v-if="insights.length > 0">
      <h4>Key Insights:</h4>
      <ul>
        <li v-for="insight in insights" :key="insight">{{ insight }}</li>
      </ul>
    </div>

    <div class="data-source">
      <small>
        Data source: Numbeo | Last updated: {{ lastUpdated }}
      </small>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';

export default {
  name: 'CostLivingChart',
  props: {
    title: {
      type: String,
      default: 'Cost of Living Comparison'
    },
    chartType: {
      type: String,
      default: 'bar' // 'bar', 'line', 'radar'
    }
  },
  data() {
    return {
      selectedMetric: 'cost_index',
      showEUComparison: false,
      citiesData: [],
      euData: null,
      chart: null,
      insights: [],
      lastUpdated: null,
      loading: true,
      error: null
    };
  },
  async mounted() {
    await this.loadData();
    this.initChart();
  },
  beforeUnmount() {
    if (this.chart) {
      this.chart.destroy();
    }
  },
  methods: {
    async loadData() {
      try {
        this.loading = true;
        
        // Load Polish cities data
        const citiesResponse = await fetch('/api/cost-living/cities');
        const citiesResult = await citiesResponse.json();
        this.citiesData = citiesResult.cities;
        this.lastUpdated = new Date(citiesResult.last_updated).toLocaleDateString();

        // Load EU comparison data
        const euResponse = await fetch('/api/cost-living/poland-vs-eu');
        const euResult = await euResponse.json();
        this.euData = euResult.eu_comparisons;
        this.insights = euResult.insights || [];

        this.loading = false;
      } catch (error) {
        console.error('Error loading cost of living data:', error);
        this.error = 'Failed to load data';
        this.loading = false;
      }
    },

    initChart() {
      const ctx = this.$refs.chartCanvas.getContext('2d');
      
      const chartConfig = {
        type: this.chartType,
        data: this.getChartData(),
        options: this.getChartOptions()
      };

      this.chart = new Chart(ctx, chartConfig);
    },

    getChartData() {
      const sortedCities = [...this.citiesData]
        .filter(city => city[this.selectedMetric] != null)
        .sort((a, b) => b[this.selectedMetric] - a[this.selectedMetric]);

      const datasets = [{
        label: this.getMetricLabel(this.selectedMetric),
        data: sortedCities.map(city => city[this.selectedMetric]),
        backgroundColor: sortedCities.map(city => this.getCityColor(city)),
        borderColor: '#2563eb',
        borderWidth: 1
      }];

      // Add EU average line if enabled
      if (this.showEUComparison && this.euData) {
        const euMetric = this.euData.find(item => 
          item.indicator_subtype === this.selectedMetric
        );
        
        if (euMetric) {
          datasets.push({
            label: 'EU Average',
            data: Array(sortedCities.length).fill(euMetric.eu_average),
            type: 'line',
            borderColor: '#dc2626',
            backgroundColor: 'rgba(220, 38, 38, 0.1)',
            borderWidth: 2,
            pointRadius: 0,
            borderDash: [5, 5]
          });
        }
      }

      return {
        labels: sortedCities.map(city => city.name_en || city.name),
        datasets
      };
    },

    getChartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: `${this.getMetricLabel(this.selectedMetric)} by City`
          },
          legend: {
            display: this.showEUComparison
          },
          tooltip: {
            callbacks: {
              afterLabel: (context) => {
                const city = this.citiesData[context.dataIndex];
                if (!city) return '';
                
                return [
                  `Voivodeship: ${city.voivodeship_en || city.voivodeship}`,
                  `Population: ${this.formatNumber(city.population)}`
                ];
              }
            }
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Cities'
            }
          },
          y: {
            title: {
              display: true,
              text: this.getMetricUnit(this.selectedMetric)
            },
            beginAtZero: this.selectedMetric !== 'local_purchasing_power_index'
          }
        }
      };
    },

    updateChart() {
      if (!this.chart) return;
      
      this.chart.data = this.getChartData();
      this.chart.options.plugins.title.text = 
        `${this.getMetricLabel(this.selectedMetric)} by City`;
      this.chart.options.scales.y.title.text = 
        this.getMetricUnit(this.selectedMetric);
      
      this.chart.update();
      this.generateInsights();
    },

    compareWithEU() {
      this.showEUComparison = !this.showEUComparison;
      this.updateChart();
    },

    getCityColor(city) {
      // Color code by voivodeship or by value
      const colors = [
        '#3b82f6', '#ef4444', '#10b981', '#f59e0b', 
        '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'
      ];
      return colors[city.voivodeship_id % colors.length] || '#6b7280';
    },

    getMetricLabel(metric) {
      const labels = {
        cost_index: 'Cost of Living Index',
        rent_index: 'Rent Index',
        groceries_index: 'Groceries Index',
        restaurant_index: 'Restaurant Index',
        local_purchasing_power_index: 'Local Purchasing Power'
      };
      return labels[metric] || metric;
    },

    getMetricUnit(metric) {
      if (metric.includes('index')) {
        return 'Index (NYC = 100)';
      }
      return 'Value';
    },

    generateInsights() {
      const values = this.citiesData
        .map(city => city[this.selectedMetric])
        .filter(val => val != null);
      
      if (values.length === 0) return;

      const max = Math.max(...values);
      const min = Math.min(...values);
      const avg = values.reduce((a, b) => a + b, 0) / values.length;

      const maxCity = this.citiesData.find(city => city[this.selectedMetric] === max);
      const minCity = this.citiesData.find(city => city[this.selectedMetric] === min);

      this.insights = [
        `${maxCity?.name_en} has the highest ${this.getMetricLabel(this.selectedMetric).toLowerCase()} (${max.toFixed(1)})`,
        `${minCity?.name_en} has the lowest ${this.getMetricLabel(this.selectedMetric).toLowerCase()} (${min.toFixed(1)})`,
        `Average across major Polish cities: ${avg.toFixed(1)}`
      ];

      // Add EU comparison insight if available
      if (this.showEUComparison && this.euData) {
        const euMetric = this.euData.find(item => 
          item.indicator_subtype === this.selectedMetric
        );
        
        if (euMetric) {
          const comparison = avg > euMetric.eu_average ? 'higher' : 'lower';
          const percentage = Math.abs(((avg - euMetric.eu_average) / euMetric.eu_average) * 100);
          
          this.insights.push(
            `Polish cities average is ${percentage.toFixed(1)}% ${comparison} than EU average (${euMetric.eu_average.toFixed(1)})`
          );
        }
      }
    },

    formatNumber(num) {
      if (!num) return 'N/A';
      return new Intl.NumberFormat().format(num);
    }
  }
};
</script>

<style scoped>
.cost-living-chart {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.chart-header h3 {
  margin: 0;
  color: #111827;
  font-size: 1.25rem;
  font-weight: 600;
}

.chart-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.chart-controls select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  font-size: 14px;
}

.eu-toggle {
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  color: #374151;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.eu-toggle:hover {
  background: #f9fafb;
}

.eu-toggle.active {
  background: #2563eb;
  color: white;
  border-color: #2563eb;
}

.chart-container {
  height: 400px;
  position: relative;
  margin-bottom: 20px;
}

.chart-insights {
  background: #f8fafc;
  padding: 16px;
  border-radius: 6px;
  margin-bottom: 16px;
}

.chart-insights h4 {
  margin: 0 0 12px 0;
  color: #374151;
  font-size: 1rem;
  font-weight: 600;
}

.chart-insights ul {
  margin: 0;
  padding-left: 20px;
}

.chart-insights li {
  margin-bottom: 8px;
  color: #4b5563;
  line-height: 1.5;
}

.data-source {
  color: #6b7280;
  font-size: 12px;
  text-align: right;
}

/* Responsive design */
@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .chart-controls {
    flex-direction: column;
    gap: 8px;
  }
  
  .chart-container {
    height: 300px;
  }
}
</style>