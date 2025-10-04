-- D1 Database Migration Script for Poland Living Standards Dashboard

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS eu_comparisons;
DROP TABLE IF EXISTS amenities_count;
DROP TABLE IF EXISTS quality_metrics;
DROP TABLE IF EXISTS crime_statistics;
DROP TABLE IF EXISTS cost_living_data;
DROP TABLE IF EXISTS cities;
DROP TABLE IF EXISTS voivodeships;

-- Create voivodeships table (16 Polish regions)
CREATE TABLE voivodeships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    name_en TEXT NOT NULL,
    nuts_code TEXT UNIQUE NOT NULL,
    population INTEGER,
    area_km2 REAL,
    capital_city TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create cities table (major Polish cities)
CREATE TABLE cities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    name_en TEXT,
    voivodeship_id INTEGER NOT NULL,
    population INTEGER,
    is_major BOOLEAN DEFAULT FALSE,
    lat REAL,
    lon REAL,
    numbeo_slug TEXT, -- For API integration
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (voivodeship_id) REFERENCES voivodeships(id)
);

-- Create cost of living data table
CREATE TABLE cost_living_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city_id INTEGER,
    data_date DATE NOT NULL,
    cost_index REAL, -- Overall cost of living index (NYC = 100)
    rent_index REAL,
    groceries_index REAL,
    restaurant_index REAL,
    local_purchasing_power_index REAL,
    
    -- Specific price points in USD
    meal_inexpensive_restaurant REAL,
    meal_for_2_midrange REAL,
    domestic_beer REAL,
    cappuccino REAL,
    milk_1l REAL,
    bread_loaf REAL,
    
    -- Housing costs
    apartment_1br_center REAL,
    apartment_1br_outside REAL,
    apartment_3br_center REAL,
    apartment_3br_outside REAL,
    
    -- Transportation
    oneway_ticket REAL,
    monthly_pass REAL,
    taxi_start REAL,
    taxi_1km REAL,
    gasoline_1l REAL,
    
    -- Utilities
    utilities_basic REAL,
    internet REAL,
    mobile_plan REAL,
    
    source TEXT DEFAULT 'numbeo',
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (city_id) REFERENCES cities(id)
);

-- Create crime statistics table
CREATE TABLE crime_statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    region_id INTEGER NOT NULL,
    region_type TEXT NOT NULL, -- 'voivodeship', 'city', 'nuts3'
    data_year INTEGER NOT NULL,
    
    -- Total counts
    total_crimes INTEGER,
    violent_crimes INTEGER,
    property_crimes INTEGER,
    
    -- Specific crime types (per 100k residents)
    homicide_rate REAL,
    assault_rate REAL,
    robbery_rate REAL,
    burglary_rate REAL,
    theft_rate REAL,
    
    -- Traffic and safety
    road_accidents INTEGER,
    road_fatalities INTEGER,
    
    -- Calculated rates
    crime_rate_per_100k REAL,
    safety_index REAL, -- Derived safety score
    
    source TEXT DEFAULT 'gus',
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create quality of life metrics table
CREATE TABLE quality_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city_id INTEGER,
    data_date DATE NOT NULL,
    
    -- Numbeo quality indices (0-100 scale)
    quality_of_life_index REAL,
    purchasing_power_index REAL,
    safety_index REAL,
    health_care_index REAL,
    cost_of_living_index REAL,
    property_price_to_income_ratio REAL,
    traffic_commute_time_index REAL,
    pollution_index REAL,
    climate_index REAL,
    
    -- EQLS derived metrics (where available)
    life_satisfaction REAL, -- 1-10 scale
    work_life_balance REAL,
    social_exclusion_risk REAL,
    
    source TEXT DEFAULT 'numbeo',
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (city_id) REFERENCES cities(id)
);

-- Create amenities count table (from OpenStreetMap via Overpass)
CREATE TABLE amenities_count (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city_id INTEGER NOT NULL,
    amenity_type TEXT NOT NULL, -- 'hospital', 'school', 'university', 'pharmacy', 'bank', 'transport'
    
    -- Raw counts
    count_total INTEGER,
    
    -- Normalized metrics
    per_100k_residents REAL,
    per_km2 REAL,
    
    -- Quality indicators
    avg_distance_to_nearest REAL, -- Average distance in meters
    
    last_updated DATE NOT NULL,
    FOREIGN KEY (city_id) REFERENCES cities(id)
);

-- Create EU comparisons table
CREATE TABLE eu_comparisons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    indicator_type TEXT NOT NULL, -- 'cost_living', 'crime_rate', 'quality_life', 'purchasing_power'
    indicator_subtype TEXT, -- specific metric like 'rent_index', 'homicide_rate'
    
    poland_value REAL NOT NULL,
    poland_city_id INTEGER, -- If city-specific comparison
    
    -- EU statistics
    eu_average REAL,
    eu_median REAL,
    eu_min REAL,
    eu_max REAL,
    
    -- Rankings
    poland_rank INTEGER,
    total_countries INTEGER,
    
    -- Percentiles
    poland_percentile REAL,
    
    data_date DATE NOT NULL,
    source TEXT DEFAULT 'eurostat',
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (poland_city_id) REFERENCES cities(id)
);

-- Create indexes for better query performance
CREATE INDEX idx_cost_living_city_date ON cost_living_data(city_id, data_date);
CREATE INDEX idx_crime_stats_region_year ON crime_statistics(region_id, region_type, data_year);
CREATE INDEX idx_quality_metrics_city_date ON quality_metrics(city_id, data_date);
CREATE INDEX idx_amenities_city_type ON amenities_count(city_id, amenity_type);
CREATE INDEX idx_eu_comparisons_indicator ON eu_comparisons(indicator_type, indicator_subtype);

-- Create views for common queries

-- View for latest cost of living data per city
CREATE VIEW v_latest_cost_living AS
SELECT 
    cld.*,
    c.name as city_name,
    c.name_en as city_name_en,
    v.name as voivodeship_name,
    v.name_en as voivodeship_name_en
FROM cost_living_data cld
JOIN cities c ON cld.city_id = c.id
JOIN voivodeships v ON c.voivodeship_id = v.id
WHERE cld.data_date = (
    SELECT MAX(data_date) 
    FROM cost_living_data cld2 
    WHERE cld2.city_id = cld.city_id
);

-- View for latest quality metrics per city
CREATE VIEW v_latest_quality_metrics AS
SELECT 
    qm.*,
    c.name as city_name,
    c.name_en as city_name_en,
    v.name as voivodeship_name
FROM quality_metrics qm
JOIN cities c ON qm.city_id = c.id
JOIN voivodeships v ON c.voivodeship_id = v.id
WHERE qm.data_date = (
    SELECT MAX(data_date) 
    FROM quality_metrics qm2 
    WHERE qm2.city_id = qm.city_id
);

-- View for latest crime statistics by voivodeship
CREATE VIEW v_latest_crime_by_voivodeship AS
SELECT 
    cs.*,
    v.name as voivodeship_name,
    v.name_en as voivodeship_name_en
FROM crime_statistics cs
JOIN voivodeships v ON cs.region_id = v.id
WHERE cs.region_type = 'voivodeship'
AND cs.data_year = (
    SELECT MAX(data_year) 
    FROM crime_statistics cs2 
    WHERE cs2.region_id = cs.region_id 
    AND cs2.region_type = 'voivodeship'
);