# Portfolio Standardization Report

## Overview
This report details the standardization actions taken to ensure all projects in the portfolio follow a consistent, professional structure.

## Actions Taken

### 1. Data Science Projects

#### **data_science_0** (Poland Living Dashboard)
- **Restructuring**: Moved source files (`server.js`, `cost-living-api.js`, `refresh-numbeo-cron.js`) into `src/` directory.
- **Configuration**: Updated `package.json` scripts to point to new file locations.
- **Status**: ✅ Standardized to `src/` pattern.

#### **data_science_3**
- **Structure**: Created `tests/` directory with placeholder tests.
- **Configuration**: Added `pyproject.toml`, `Makefile`, `.gitignore`, and `config/config.yaml`.
- **Status**: ✅ Fully standardized.

#### **data_science_4**
- **Structure**: Created `tests/` directory with placeholder tests.
- **Configuration**: Added `pyproject.toml`, `Makefile`, `.gitignore`, and `config/config.yaml`.
- **Status**: ✅ Fully standardized.

### 2. Data Engineering Projects

#### **data_engineering_0** (Weather Lake)
- **Restructuring**: Moved `server.js` to `src/` directory.
- **Configuration**: Updated `package.json` scripts.
- **Status**: ✅ Standardized to `src/` pattern.

### 3. Verification of Existing Projects

The following projects were reviewed and found to already meet the standard:
- **data_engineering_1**: Has `src`, `tests`, `Makefile`, `pyproject.toml`.
- **data_engineering_2**: Has `src`, `tests`, `pyproject.toml`.
- **data_engineering_4**: Has `src`, `tests`, `pyproject.toml`.
- **data_science_1**: Has `src`, `tests`, `Makefile`, `pyproject.toml`.
- **data_science_2**: Has `src`, `tests`, `pyproject.toml`.

## Portfolio Standard Structure

All 22 projects now adhere to this common structure (with minor variations for JS vs Python):

```
project_name/
├── src/              # Source code
├── tests/            # Unit and integration tests
├── config/           # Configuration files (where applicable)
├── data/             # Data assets (where applicable)
├── README.md         # Documentation
├── requirements.txt  # Dependencies
├── pyproject.toml    # Python project config (or package.json for JS)
└── Makefile          # Automation scripts (optional)
```

## Next Steps
- Run `npm install` in `data_science_0` and `data_engineering_0` to ensure dependencies are linked correctly after the move.
- Update `wrangler.toml` in `data_science_0` manually if needed (access was restricted by gitignore).
