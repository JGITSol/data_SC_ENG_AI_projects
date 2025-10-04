-- Locations table for Polish cities
CREATE TABLE locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Hourly forecast data
CREATE TABLE hourly_forecast (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER NOT NULL,
    timestamp DATETIME NOT NULL,
    temp_c REAL,
    wind_mps REAL,
    humidity_pct REAL,
    precip_mm REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES locations(id),
    UNIQUE(location_id, timestamp)
);

-- Daily forecast summaries
CREATE TABLE daily_forecast (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER NOT NULL,
    date DATE NOT NULL,
    temp_min_c REAL,
    temp_max_c REAL,
    precip_mm REAL,
    wind_max_mps REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES locations(id),
    UNIQUE(location_id, date)
);

-- Indexes for performance
CREATE INDEX idx_hourly_location_time ON hourly_forecast(location_id, timestamp);
CREATE INDEX idx_daily_location_date ON daily_forecast(location_id, date);
CREATE INDEX idx_locations_slug ON locations(slug);

-- Insert initial Polish cities
INSERT INTO locations (slug, name, lat, lon) VALUES 
('bialystok', 'Białystok', 53.1325, 23.1688),
('warsaw', 'Warszawa', 52.2297, 21.0122),
('krakow', 'Kraków', 50.0647, 19.9450),
('gdansk', 'Gdańsk', 54.3520, 18.6466),
('wroclaw', 'Wrocław', 51.1079, 17.0385);