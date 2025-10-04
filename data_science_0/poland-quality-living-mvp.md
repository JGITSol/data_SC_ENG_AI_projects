# Poland Quality of Living Portfolio Project - MVP Implementation

## Project: Poland Living Standards vs EU Dashboard

### Data Sources & APIs
- **Numbeo API**: Cost of living, crime perception, quality of life indices [web:74][web:77]
- **Eurostat Regional Crime API**: NUTS-3 police-recorded offences [web:58][web:69]
- **GUS BDL API**: Polish regional crime & living statistics [web:56][web:59]
- **Overpass API**: Amenities (hospitals, schools, transport) per city [web:43][web:44]
- **EQLS Data**: Quality of life survey data for EU comparison [web:80][web:81]

### Core Implementation Stack
- **Frontend**: Cloudflare Pages (React/Vue SPA)
- **API**: Cloudflare Pages Functions (serverless)
- **Database**: Cloudflare D1 (SQLite)
- **Scheduler**: Cloudflare Workers Cron Triggers
- **Hosting**: Free Cloudflare tier

### MVP Features

#### 1. Cost of Living Comparison
- Compare major Polish cities vs EU capitals
- Rent, groceries, transport, utilities indices
- Real-time Numbeo API integration with D1 caching

#### 2. Crime & Safety Analysis  
- Police-recorded crimes per 100k residents
- Property crimes, violent crimes, traffic accidents
- Polish voivodeships vs EU NUTS-3 regions

#### 3. Quality of Life Metrics
- Healthcare access, education quality
- Transport connectivity, environmental quality
- Work-life balance indicators

#### 4. Regional Deep-Dive
- 16 Polish voivodeships breakdown
- 1-3 major cities per region analysis
- Interactive choropleth maps with NUTS boundaries

## File Structure

```
poland-living-dashboard/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CostLivingChart.vue
│   │   │   ├── CrimeStatsMap.vue
│   │   │   ├── QualityLifeRadar.vue
│   │   │   └── RegionalComparison.vue
│   │   ├── data/
│   │   │   ├── voivodeships.json
│   │   │   ├── major-cities.json
│   │   │   └── eu-comparators.json
│   │   └── App.vue
│   ├── public/
│   └── package.json
├── functions/
│   ├── api/
│   │   ├── cost-living.js
│   │   ├── crime-stats.js
│   │   ├── quality-metrics.js
│   │   └── regional-data.js
│   └── scheduled/
│       ├── refresh-numbeo.js
│       ├── fetch-eurostat.js
│       └── update-gus.js
├── data/
│   ├── migrations/
│   │   ├── 001_create_tables.sql
│   │   └── 002_seed_locations.sql
│   └── scripts/
│       ├── setup-database.js
│       └── initial-data-load.js
├── wrangler.toml
└── README.md
```

## Database Schema

```sql
-- D1 SQLite Tables

CREATE TABLE voivodeships (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    nuts_code TEXT UNIQUE,
    population INTEGER,
    area_km2 REAL,
    capital_city TEXT
);

CREATE TABLE cities (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    voivodeship_id INTEGER,
    population INTEGER,
    is_major BOOLEAN DEFAULT FALSE,
    lat REAL,
    lon REAL,
    FOREIGN KEY (voivodeship_id) REFERENCES voivodeships(id)
);

CREATE TABLE cost_living_data (
    id INTEGER PRIMARY KEY,
    city_id INTEGER,
    data_date DATE,
    cost_index REAL,
    rent_index REAL,
    groceries_index REAL,
    restaurant_index REAL,
    purchasing_power_index REAL,
    source TEXT DEFAULT 'numbeo',
    FOREIGN KEY (city_id) REFERENCES cities(id)
);

CREATE TABLE crime_statistics (
    id INTEGER PRIMARY KEY,
    region_id INTEGER,
    region_type TEXT, -- 'voivodeship', 'city', 'nuts3'
    data_year INTEGER,
    total_crimes INTEGER,
    violent_crimes INTEGER,
    property_crimes INTEGER,
    crime_rate_per_100k REAL,
    source TEXT DEFAULT 'gus'
);

CREATE TABLE quality_metrics (
    id INTEGER PRIMARY KEY,
    city_id INTEGER,
    data_date DATE,
    healthcare_index REAL,
    safety_index REAL,
    traffic_index REAL,
    pollution_index REAL,
    climate_index REAL,
    FOREIGN KEY (city_id) REFERENCES cities(id)
);

CREATE TABLE amenities_count (
    id INTEGER PRIMARY KEY,
    city_id INTEGER,
    amenity_type TEXT, -- 'hospital', 'school', 'transport'
    count_total INTEGER,
    per_100k_residents REAL,
    last_updated DATE,
    FOREIGN KEY (city_id) REFERENCES cities(id)
);

CREATE TABLE eu_comparisons (
    id INTEGER PRIMARY KEY,
    indicator_type TEXT, -- 'cost_living', 'crime_rate', 'quality_life'
    poland_value REAL,
    eu_average REAL,
    eu_median REAL,
    poland_rank INTEGER,
    total_countries INTEGER,
    data_date DATE
);
```

## API Endpoints

### `/api/cost-living`
- `GET /api/cost-living/cities` - All Polish cities with cost data
- `GET /api/cost-living/compare/:city1/:city2` - Compare two cities
- `GET /api/cost-living/poland-vs-eu` - Poland vs EU averages

### `/api/crime-stats` 
- `GET /api/crime-stats/voivodeships` - Crime by voivodeship
- `GET /api/crime-stats/cities/:voivodeship` - Cities in voivodeship
- `GET /api/crime-stats/trends/:region/:years` - Historical trends

### `/api/quality-metrics`
- `GET /api/quality-metrics/overview` - National overview
- `GET /api/quality-metrics/city/:cityId` - City-specific metrics
- `GET /api/quality-metrics/rankings` - Best/worst rankings

### `/api/regional-data`
- `GET /api/regional-data/voivodeships` - All voivodeship summaries
- `GET /api/regional-data/details/:voivodeshipId` - Detailed breakdown
- `GET /api/regional-data/amenities/:cityId` - Amenity counts

## Scheduled Jobs (Cron Triggers)

### Daily Updates
```javascript
// functions/scheduled/refresh-numbeo.js
export default {
  async scheduled(event, env, ctx) {
    // Fetch latest Numbeo data for Polish cities
    // Update cost_living_data table
    // Rate limit: 1000 API calls/month on basic plan
  }
}
```

### Weekly Updates  
```javascript
// functions/scheduled/fetch-eurostat.js
export default {
  async scheduled(event, env, ctx) {
    // Fetch EU crime statistics via NUTS-3 API
    // Update crime_statistics table for EU comparisons
  }
}
```

### Monthly Updates
```javascript
// functions/scheduled/update-gus.js  
export default {
  async scheduled(event, env, ctx) {
    // Fetch Polish regional statistics from GUS BDL
    // Update voivodeship and city-level data
  }
}
```

## Major Polish Cities by Voivodeship

### Target Cities (1-3 per voivodeship):

1. **Mazowieckie**: Warsaw, Radom
2. **Śląskie**: Katowice, Kraków (nearby), Częstochowa  
3. **Wielkopolskie**: Poznań, Kalisz
4. **Małopolskie**: Kraków, Tarnów
5. **Dolnośląskie**: Wrocław, Wałbrzych
6. **Łódzkie**: Łódź, Piotrków Trybunalski
7. **Zachodniopomorskie**: Szczecin, Koszalin
8. **Lubelskie**: Lublin, Zamość
9. **Podkarpackie**: Rzeszów, Przemyśl
10. **Warmińsko-mazurskie**: Olsztyn, Elbląg
11. **Kujawsko-pomorskie**: Bydgoszcz, Toruń
12. **Pomorskie**: Gdańsk, Gdynia
13. **Podlaskie**: Białystok
14. **Świętokrzyskie**: Kielce
15. **Lubuskie**: Gorzów Wielkopolski, Zielona Góra
16. **Opolskie**: Opole

## Implementation Timeline (48 hours)

### Day 1 (24 hours)
**Hours 1-8**: Setup & Infrastructure
- Initialize Cloudflare project
- Create D1 database and run migrations
- Setup basic Pages Functions structure
- Configure Wrangler for deployment

**Hours 9-16**: Data Pipeline  
- Implement Numbeo API integration
- Setup GUS BDL API calls for Polish data
- Create initial data loading scripts
- Test Eurostat crime API integration

**Hours 17-24**: Core APIs
- Build cost-living endpoints
- Implement crime statistics API
- Create regional comparison logic
- Setup basic caching with D1

### Day 2 (24 hours)
**Hours 25-32**: Frontend Development
- Create Vue.js/React SPA structure
- Build cost of living comparison charts
- Implement interactive maps for regions
- Add city selection and filtering

**Hours 33-40**: Quality & Polish
- Add quality of life metrics dashboard
- Implement amenities counting via Overpass
- Create EU vs Poland comparison views
- Setup scheduled data refresh jobs

**Hours 41-48**: Deployment & Testing
- Deploy to Cloudflare Pages
- Configure cron triggers for data updates
- Test all API endpoints and UI flows
- Create documentation and README

## Key Features for Portfolio

### 1. Technical Depth
- Real-time API integrations (Numbeo, Eurostat, GUS)
- Efficient caching strategy with D1
- Scheduled data pipeline automation
- Responsive web design with interactive charts

### 2. Data Science Elements
- Statistical comparisons (percentiles, z-scores)
- Trend analysis and forecasting
- Multi-dimensional quality of life scoring
- Correlation analysis between metrics

### 3. European Context
- NUTS regional classification usage
- EU policy-relevant indicators
- Cross-border data harmonization
- Multilingual support (Polish/English)

### 4. Production Ready
- Error handling and fallbacks
- API rate limiting and caching
- Mobile-responsive design
- SEO-optimized with meta tags

This MVP showcases Poland's position within Europe across multiple living standard dimensions while demonstrating modern full-stack development skills using serverless architecture.