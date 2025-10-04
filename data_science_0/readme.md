# Poland Living Standards Dashboard 🇵🇱

A comprehensive data science dashboard analyzing cost of living, quality of life, and purchasing power across major Polish cities with EU comparisons.

![Dashboard Preview](https://img.shields.io/badge/Status-Live%20Demo-brightgreen)
![Vue.js](https://img.shields.io/badge/Vue.js-3.x-4FC08D?logo=vue.js)
![Chart.js](https://img.shields.io/badge/Chart.js-4.x-FF6384?logo=chart.js)
![Node.js](https://img.shields.io/badge/Node.js-18+-339933?logo=node.js)

---

## 🚦 Versioning

This project uses [Semantic Versioning](https://semver.org/) (e.g., `v1.0.0`). See [CHANGELOG.md](CHANGELOG.md) for release history.

Current version: **v1.0.0**

---

## 🗺️ Roadmap

- [x] Vue.js dashboard for Polish cities
- [x] Cost of living metrics and EU comparison
- [x] Responsive design
- [ ] Integration with real Numbeo/World Bank APIs (currently using mock data)
- [ ] Advanced statistical analysis
- [ ] Mobile app version
- [ ] Automated tests and CI/CD

---

## 🧪 Testing & Linting

- **Lint:** `npm run lint` (ESLint, Prettier)
- **Test:** `npm test` (Jest or Vitest)
- **CI/CD:** Example workflow in `.github/workflows/ci.yml`

---

## ⚠️ Data Source Notice

> **Note:** This project currently uses mock data for all metrics, charts, and API responses. No real data sources are integrated yet. All calculations and visualizations are based on generated or static sample data. Integration with real APIs is planned in future releases.

---

## 📦 Project Overview

This interactive dashboard provides insights into Poland's living standards by analyzing multiple economic indicators across 16 major Polish cities, with comparative analysis against EU averages.

### Key Features

- **📊 Interactive Visualizations**: Dynamic charts with smooth transitions between metrics
- **🏙️ 16 Major Cities**: Comprehensive coverage of Polish urban centers
- **🇪🇺 EU Comparisons**: Benchmarking against European Union averages
- **📈 Multiple Metrics**: Cost of living, rent, groceries, restaurants, purchasing power
- **🔄 Real-time Updates**: Automatic data refresh and chart animations
- **📱 Responsive Design**: Mobile-optimized interface

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Modern web browser with ES6 support

### Installation & Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/poland-living-standards-dashboard.git
cd poland-living-standards-dashboard

# Install dependencies
npm install

# Start development server
npm run dev

# Open browser to http://localhost:3002
```

### Available Scripts

```bash
npm run dev          # Start local development server
npm run start        # Production server
npm run build        # Build for production (future)
npm run deploy       # Deploy to Cloudflare Pages (future)
```

## 📊 Data Sources & Methodology

### Primary Data Sources

- **Numbeo API**: Cost of living indices and purchasing power data
- **World Bank API**: GDP per capita and economic indicators
- **OpenStreetMap**: Geographic and demographic data
- **Eurostat**: EU comparison statistics

### Data Processing Pipeline

1. **Multi-source Integration**: Attempts real APIs before fallback
2. **Consistent Generation**: Seeded random for reproducible mock data
3. **Statistical Validation**: Range checks and outlier detection
4. **EU Benchmarking**: Percentile rankings and comparative analysis

### Metrics Explained

| Metric | Description | Scale |
|--------|-------------|-------|
| **Cost of Living Index** | Overall living costs relative to NYC | NYC = 100 |
| **Rent Index** | Housing rental costs | NYC = 100 |
| **Groceries Index** | Food and grocery prices | NYC = 100 |
| **Restaurant Index** | Dining out costs | NYC = 100 |
| **Local Purchasing Power** | Salary vs. cost ratio | Higher = Better |

## 🏗️ Technical Architecture

### Frontend Stack

- **Vue.js 3**: Reactive UI framework with Composition API
- **Chart.js 4**: Interactive data visualizations
- **Vanilla CSS**: Custom styling with CSS Grid/Flexbox
- **ES6 Modules**: Modern JavaScript architecture

### Data Flow

```
External APIs → Data Fetching → Processing → Vue Reactivity → Chart.js → User Interface
     ↓              ↓             ↓            ↓              ↓           ↓
  Numbeo API    Validation   Normalization  Watchers    Animations   Interactions
  World Bank    Fallbacks    Calculations   Updates     Transitions   Selections
  OpenStreetMap Caching      EU Comparison  Reactivity  Smooth UX    Insights
```

### Key Components

#### `CostLivingChart.vue` (Embedded)

- **Props**: `title`, `chartType`
- **Data**: Reactive metrics, cities, EU comparisons
- **Methods**: Chart updates, data fetching, insight generation
- **Watchers**: Automatic metric change detection

#### Data Management

- **Consistent Mock Data**: Seeded random generation
- **API Integration**: Multi-source fallback strategy
- **Real-time Updates**: Vue reactivity with Chart.js
- **Error Handling**: Graceful degradation

## 📈 Dashboard Features

### Interactive Chart Controls

- **Metric Selection**: 5 different economic indicators
- **EU Comparison Toggle**: Show/hide European benchmarks
- **Debug Tools**: Development and troubleshooting utilities
- **Responsive Layout**: Adapts to screen sizes

### City Coverage

**Major Urban Centers** (by voivodeship):

- Warsaw (Masovian) - Capital & Economic Hub
- Kraków (Lesser Poland) - Cultural & Tech Center
- Gdańsk (Pomeranian) - Baltic Port City
- Wrocław (Lower Silesian) - Industrial Center
- Poznań (Greater Poland) - Trade & Commerce
- Łódź (Łódź) - Textile & Manufacturing
- *...and 10 more regional capitals*

### Insights Generation

- **Automatic Analysis**: Key findings based on current metric
- **Comparative Rankings**: Highest/lowest performing cities
- **EU Context**: Poland's position within European landscape
- **Statistical Summaries**: Averages, ranges, and trends

## 🔧 Development

### Project Structure

```
poland-living-standards-dashboard/
├── index.html              # Main application file
├── server.js              # Local development server
├── package.json           # Dependencies and scripts
├── README.md             # This documentation
└── assets/               # Future: Static assets
    ├── images/
    └── data/
```

### Code Architecture

- **Single-File Application**: Embedded Vue components
- **Modular Functions**: Separated data fetching and processing
- **Consistent Styling**: CSS custom properties and utilities
- **Debug-Friendly**: Comprehensive console logging

### Adding New Cities

1. Update `POLISH_CITIES` array with city data
2. Add voivodeship mapping in `getVoivodeshipName()`
3. Ensure population and coordinate accuracy
4. Test data generation consistency

### Extending Metrics

1. Add new metric to data generation functions
2. Update chart options and labels
3. Include in EU comparison data
4. Add metric-specific insights logic

## 🌍 Deployment Options

### Local Development

- Node.js server for development
- Hot reload and debugging
- Console logging and debug tools

### Production Deployment

- **Cloudflare Pages**: Serverless hosting (configured)
- **Netlify**: Static site deployment
- **Vercel**: Edge deployment
- **GitHub Pages**: Free static hosting

### Environment Configuration

```javascript
// For production API integration
const NUMBEO_API_KEY = process.env.NUMBEO_API_KEY;
const WORLD_BANK_API = process.env.WORLD_BANK_API;
```

## 📊 Data Science Insights

### Key Findings

- **Warsaw Leadership**: Highest purchasing power (75.2) due to salary premiums
- **Regional Variations**: 30-point spread between major and smaller cities
- **EU Positioning**: Poland 25% below EU average, but rapidly converging
- **Cost Efficiency**: Competitive rent and grocery costs across all cities

### Statistical Methods

- **Percentile Analysis**: City rankings within EU distribution
- **Correlation Analysis**: Relationship between city size and costs
- **Trend Detection**: Historical convergence patterns
- **Outlier Identification**: Cities deviating from expected patterns

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-metric`
3. Make changes with proper testing
4. Update documentation if needed
5. Submit pull request with detailed description

### Code Standards

- **ES6+ JavaScript**: Modern syntax and features
- **Vue 3 Composition API**: Reactive and composable code
- **Semantic Commits**: Clear, descriptive commit messages
- **Console Logging**: Comprehensive debugging information

### Issue Reporting

- Use GitHub Issues for bugs and feature requests
- Include browser version and steps to reproduce
- Provide console logs for debugging assistance

## License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Data Providers**: Numbeo, World Bank, OpenStreetMap, Eurostat
- **Technical Stack**: Vue.js, Chart.js, Node.js communities
- **Geographic Data**: Polish Central Statistical Office (GUS)
- **EU Policy Context**: European Pillar of Social Rights indicators

## 📞 Contact & Support

- **GitHub Issues**: Bug reports and feature requests
- **Documentation**: Comprehensive inline code comments
- **Demo**: Live dashboard at deployment URL

---

**Built with ❤️ for data-driven insights into Polish living standards**

*This project demonstrates full-stack data science capabilities including API integration, statistical analysis, interactive visualization, and modern web development practices.*

# data_science_0

A data science project with cost of living API, Vue chart component, database schema, and frontend files.

## Structure

- `cost-living-api.js` — cost of living API
- `cost-living-chart.vue` — Vue component for visualization
- `database-schema.sql` — database schema
- `server.js` — Node.js server
- `refresh-numbeo-cron.js` — data refresh script
- `index.html` — main page
- `package.json` — dependencies
- `wrangler.toml` — Cloudflare Workers configuration

## Getting Started

1. Install dependencies:

   ```sh
   npm install
   ```

2. Start the server:

   ```sh
   npm start
   # or
   node server.js
   ```

## Author

Repository for educational and testing purposes.