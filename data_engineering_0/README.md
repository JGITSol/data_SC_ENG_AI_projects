# Poland Quality Living MVP (Data Engineering)

## Overview
A serverless ETL pipeline designed to aggregate real-time economic and weather data for Polish cities. This project demonstrates a modern "Data Lake" architecture using Cloudflare's edge ecosystem.

## Features
- **Serverless ETL**: Runs on Cloudflare Workers (Cron Triggers).
- **Edge Database**: Stores structured data in Cloudflare D1 (SQLite at the Edge).
- **Object Storage**: Archives raw JSON snapshots in Cloudflare R2.
- **API Access**: Provides a RESTful API for querying aggregated metrics.

## Tech Stack
- **Runtime**: Cloudflare Workers (TypeScript)
- **Database**: Cloudflare D1
- **Storage**: Cloudflare R2
- **Scheduling**: Cron Triggers

## Getting Started

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Local Development**
   ```bash
   npx wrangler dev
   ```

3. **Deploy**
   ```bash
   npx wrangler deploy
   ```

## License
MIT
