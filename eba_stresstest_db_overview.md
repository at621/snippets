# EBA Transparency Exercise 2025 Database Documentation

## Overview

This database contains data from the European Banking Authority (EBA) Transparency Exercise 2025, providing detailed information on European banks' financial positions, credit risk exposures, and stress test results. The data supports regulatory oversight, market transparency, and financial stability analysis.

**Data Period**: December 2024 (with historical comparisons)  
**Scope**: Major European banks under ECB supervision  
**Purpose**: Credit risk assessment, capital adequacy evaluation, stress testing

## Database Schema

### Logical Architecture

```
Main Data Tables:
├── tra_cre_irb (534K records)    - Credit Risk IRB Approach
├── tra_cre_sta (595K records)    - Credit Risk Standardized Approach  
└── tra_oth (64K records)         - Other Financial Metrics

Reference Tables:
├── sdd                           - Data Dictionary (Item definitions)
├── list_of_banks                 - Bank Directory
├── scenario                      - Stress Test Scenarios
├── country                       - Country Codes & Names
├── portfolio                     - Credit Portfolio Types
├── exposure                      - Exposure Categories
├── ifrs9_stages                  - IFRS9 Credit Loss Stages
├── perf_status                   - Performance Status
├── business_cards_2018           - Bank Business Information
├── fi_business_cards_2018        - Financial Institution Cards
└── dimensions_used               - Metadata Dimensions
```

### Table Dependencies

**Primary Flow:**
1. `list_of_banks` → Main data tables (via lei_code)
2. Reference tables → Main data tables (via coded fields)
3. `sdd` → Main data tables (via item codes)

## Table Definitions

### Main Data Tables

#### tra_cre_irb
**Credit Risk - Internal Ratings Based Approach**

| Field | Type | Description |
|-------|------|-------------|
| id | SERIAL PRIMARY KEY | Auto-increment identifier |
| country_code | VARCHAR(2) NOT NULL | ISO country code |
| lei_code | VARCHAR(20) NOT NULL | Legal Entity Identifier |
| bank_name | VARCHAR(70) | Bank name |
| period | INTEGER | Reporting period (YYYYMM format) |
| item | INTEGER | Data item code (links to sdd table) |
| scenario | SMALLINT | Stress test scenario (0=actual, 1=baseline, 2=adverse, etc.) |
| portfolio | SMALLINT | Portfolio type (1=SA, 2=IRB, 3=F-IRB, 4=A-IRB) |
| ifrs9_stages | SMALLINT | IFRS9 stage (0=no breakdown, 1=Stage 1, 2=Stage 2, 3=Stage 3) |
| exposure | SMALLINT | Exposure category code |
| country | SMALLINT | Counterparty country code |
| country_rank | SMALLINT | Country ranking |
| perf_status | SMALLINT | Performance status (0=no breakdown, 1=performing, 2=non-performing) |
| amount | DECIMAL(25,10) | Amount in millions EUR |

#### tra_cre_sta  
**Credit Risk - Standardized Approach**

Same structure as `tra_cre_irb` - represents credit risk data calculated using the standardized approach rather than internal models.

#### tra_oth
**Other Financial Metrics**

| Field | Type | Description |
|-------|------|-------------|
| id | SERIAL PRIMARY KEY | Auto-increment identifier |
| country_code | VARCHAR(2) NOT NULL | ISO country code |
| lei_code | VARCHAR(20) NOT NULL | Legal Entity Identifier |
| bank_name | VARCHAR(70) | Bank name |
| period | INTEGER | Reporting period (YYYYMM format) |
| item | INTEGER | Data item code (links to sdd table) |
| scenario | SMALLINT | Stress test scenario |
| fact_char | VARCHAR(30) | Fact characteristics |
| amount | DECIMAL(25,10) | Amount in millions EUR |

### Reference Tables

#### sdd
**Data Dictionary - Item Definitions**

| Field | Type | Description |
|-------|------|-------------|
| id | SERIAL PRIMARY KEY | Auto-increment identifier |
| collection | VARCHAR(6) | Collection identifier (ST2025) |
| template | VARCHAR(11) | Template name |
| item | INTEGER | Item code (primary business key) |
| item_st_2023 | DECIMAL(10,1) | 2023 mapping |
| item_st_2021 | DECIMAL(8,1) | 2021 mapping |
| item_st_2018 | DECIMAL(8,1) | 2018 mapping |
| item_st_2016 | INTEGER | 2016 mapping |
| category | VARCHAR(31) | Item category |
| label | TEXT | Human-readable description |

**Key Categories:**
- Transparency - CAP (Capital measures)
- Transparency - P&L (Profit & Loss)  
- Transparency - REA (Risk Exposure Amounts)
- Transparency - CR (Credit Risk)
- Transparency - summary

#### list_of_banks
**Bank Directory**

| Field | Type | Description |
|-------|------|-------------|
| id | SERIAL PRIMARY KEY | Auto-increment identifier |
| country | VARCHAR(2) | Country code |
| desc_country | VARCHAR(11) | Country name |
| lei_code | VARCHAR(20) NOT NULL | Legal Entity Identifier (business key) |
| name | VARCHAR(65) | Official bank name |
| bank_specific_footnote | TEXT | Special notes about the bank |

### Lookup Tables

#### scenario
**Stress Test Scenarios**

| Code | Label | Description |
|------|-------|-------------|
| 0 | No breakdown by scenario | Aggregate across all scenarios |
| 1 | Actual figures | Historical actual results |
| 2 | Baseline scenario | Regulatory baseline projection |
| 3 | Adverse scenario | Stress test adverse scenario |
| 11 | Restated | Restated/adjusted figures |

#### country  
**Country Codes & Names**

| Code | Label | ISO_Code | Description |
|------|-------|----------|-------------|
| 0 | Total / No breakdown | 00 | Aggregate across countries |
| 1 | Austria | AT | Austria |
| 2 | Belgium | BE | Belgium |
| 3 | Bulgaria | BG | Bulgaria |
| ... | ... | ... | (Additional EU countries) |

#### portfolio
**Credit Portfolio Types**

| Code | Label | Description |
|------|-------|-------------|
| 0 | Total / No breakdown by portfolio | All portfolio types combined |
| 1 | SA | Standardized Approach |
| 2 | IRB | Internal Ratings Based |
| 3 | F-IRB | Foundation IRB |
| 4 | A-IRB | Advanced IRB |
| 10 | SEC-IRBA | Securitization IRBA |
| 11 | SEC-SA | Securitization SA |
| 12 | SEC-ERBA | Securitization ERBA |
| 13 | SEC-IAA | Securitization IAA |

#### exposure
**Exposure Categories**

| Code | Label | Description |
|------|-------|-------------|
| 0 | TOTAL / No breakdown by Exposure | All exposure types |
| 1110 | Public sector - Central governments or central banks | Sovereign exposures |
| 1120 | Public sector - Central governments or central banks (QCCP) | Qualified CCP exposures |
| 1200 | Public sector - Regional governments or local authorities | Sub-sovereign public sector |
| 1300 | Public sector - Public sector entities | Other public entities |
| ... | ... | (Additional exposure categories) |

#### ifrs9_stages
**IFRS9 Credit Loss Stages**

| Code | Label | Description |
|------|-------|-------------|
| 0 | No breakdown by IFRS9_Stages | All stages combined |
| 1 | Stage 1 | 12-month expected credit losses |
| 2 | Stage 2 | Lifetime expected credit losses (not credit-impaired) |
| 3 | Stage 3 | Lifetime expected credit losses (credit-impaired) |

#### perf_status
**Performance Status**

| Code | Label | Description |
|------|-------|-------------|
| 0 | No breakdown by Perf_status | All performance levels |
| 1 | Performing / not defaulted | Healthy exposures |
| 2 | Non Performing / Defaulted | Distressed exposures |

## Database Relationships & Keys

### Primary Keys by Table

**Main Data Tables:**
- `tra_cre_irb.id` (SERIAL) - Auto-generated primary key
- `tra_cre_sta.id` (SERIAL) - Auto-generated primary key  
- `tra_oth.id` (SERIAL) - Auto-generated primary key

**Reference Tables:**
- `sdd.id` (SERIAL) - Auto-generated primary key
- `list_of_banks.id` (SERIAL) - Auto-generated primary key
- `scenario.scenario` (SMALLINT) - Business code primary key
- `country.country` (SMALLINT) - Business code primary key
- `portfolio.portfolio` (SMALLINT) - Business code primary key
- `exposure.exposure` (SMALLINT) - Business code primary key
- `ifrs9_stages.ifrs9_stages` (SMALLINT) - Business code primary key
- `perf_status.perf_status` (SMALLINT) - Business code primary key

**Business Cards Tables:**
- `business_cards_2018.id` (SERIAL) - Auto-generated primary key
- `fi_business_cards_2018.id` (SERIAL) - Auto-generated primary key
- `dimensions_used.id` (SERIAL) - Auto-generated primary key

### Foreign Key Relationships

#### tra_cre_irb & tra_cre_sta Foreign Keys:
```sql
-- Bank identification
lei_code → list_of_banks.lei_code (VARCHAR(20))

-- Data item definition  
item → sdd.item (INTEGER)

-- Lookup dimensions
scenario → scenario.scenario (SMALLINT)
country → country.country (SMALLINT)  
portfolio → portfolio.portfolio (SMALLINT)
exposure → exposure.exposure (SMALLINT)
ifrs9_stages → ifrs9_stages.ifrs9_stages (SMALLINT)
perf_status → perf_status.perf_status (SMALLINT)
```

#### tra_oth Foreign Keys:
```sql  
-- Bank identification
lei_code → list_of_banks.lei_code (VARCHAR(20))

-- Data item definition
item → sdd.item (INTEGER)

-- Lookup dimensions  
scenario → scenario.scenario (SMALLINT)
```

### Business Keys (Natural Keys)

**Important**: While technical primary keys use auto-generated IDs, the business logic relies on natural keys:

**Bank Identification:**
- `lei_code` - Legal Entity Identifier (globally unique)
- `bank_name` - Human-readable bank name

**Data Item Identification:**
- `item` - Numeric code defining what metric is being reported
- Combined with `sdd.item` for full definition

**Dimensional Analysis Keys:**
- `period` - Time dimension (YYYYMM format)
- `scenario` - Stress test scenario
- `country_code` - Geographic dimension (ISO codes)

### Composite Business Keys

**Main data records are uniquely identified by:**
```sql
-- For tra_cre_irb / tra_cre_sta
(lei_code, period, item, scenario, portfolio, ifrs9_stages, exposure, country, country_rank, perf_status)

-- For tra_oth  
(lei_code, period, item, scenario, fact_char)
```

### Detailed Relationship Mapping

#### 1. Bank Master Data Flow
```
list_of_banks (Master bank registry)
    |
    | lei_code (FK)
    ↓
tra_cre_irb, tra_cre_sta, tra_oth (Transaction data)
    |
    | lei_code (FK)  
    ↓
business_cards_2018, fi_business_cards_2018 (Bank details)
```

#### 2. Data Definition Flow  
```
sdd (Data dictionary)
    |
    | item (FK)
    ↓
tra_cre_irb, tra_cre_sta, tra_oth (Uses item codes)
```

#### 3. Dimensional Lookup Flow
```
Reference Tables          Main Data Tables
scenario ──────────────→ tra_cre_irb.scenario
country ───────────────→ tra_cre_irb.country  
portfolio ─────────────→ tra_cre_irb.portfolio
exposure ──────────────→ tra_cre_irb.exposure
ifrs9_stages ──────────→ tra_cre_irb.ifrs9_stages
perf_status ───────────→ tra_cre_irb.perf_status
```

### Referential Integrity Constraints

**If implementing formal foreign keys:**

```sql
-- Main data table constraints
ALTER TABLE tra_cre_irb 
    ADD CONSTRAINT fk_tra_cre_irb_lei 
    FOREIGN KEY (lei_code) REFERENCES list_of_banks(lei_code);
    
ALTER TABLE tra_cre_irb 
    ADD CONSTRAINT fk_tra_cre_irb_item 
    FOREIGN KEY (item) REFERENCES sdd(item);
    
ALTER TABLE tra_cre_irb 
    ADD CONSTRAINT fk_tra_cre_irb_scenario 
    FOREIGN KEY (scenario) REFERENCES scenario(scenario);
    
-- Repeat for other dimensions...
```

### Data Validation Rules

**Orphan Record Prevention:**
- Every `lei_code` in main data must exist in `list_of_banks`
- Every `item` in main data must exist in `sdd`  
- Every lookup code must exist in corresponding reference table

**Business Logic Validation:**
- `period` format: YYYYMM (e.g., 202412)
- `scenario` values: 0, 1, 2, 3, 11 (from scenario table)
- `country_code` must be valid ISO codes
- `amount` can be negative (losses) or positive

### Join Patterns

#### Complete Bank Analysis Query Template:
```sql
SELECT 
    b.name as bank_name,
    b.desc_country as bank_country,
    s.label as scenario_name,
    c.label as counterparty_country,
    p.label as portfolio_type,
    e.label as exposure_type,
    i.label as ifrs9_stage,
    ps.label as performance_status,
    d.label as metric_definition,
    t.amount
FROM tra_cre_irb t
    JOIN list_of_banks b ON t.lei_code = b.lei_code
    JOIN sdd d ON t.item = d.item
    JOIN scenario s ON t.scenario = s.scenario
    JOIN country c ON t.country = c.country
    JOIN portfolio p ON t.portfolio = p.portfolio  
    JOIN exposure e ON t.exposure = e.exposure
    JOIN ifrs9_stages i ON t.ifrs9_stages = i.ifrs9_stages
    JOIN perf_status ps ON t.perf_status = ps.perf_status
WHERE t.period = 202412;
```

#### Simplified Bank Summary:
```sql
SELECT 
    b.name,
    d.label as metric,
    SUM(t.amount) as total
FROM tra_oth t
    JOIN list_of_banks b ON t.lei_code = b.lei_code
    JOIN sdd d ON t.item = d.item
WHERE t.scenario = 1  -- Actual figures
GROUP BY b.lei_code, b.name, t.item, d.label;
```

### Indexing Strategy for Relationships

**Primary Indexes (Performance Critical):**
```sql
-- Main data access patterns
CREATE INDEX idx_tra_cre_irb_lei_period ON tra_cre_irb(lei_code, period);
CREATE INDEX idx_tra_cre_irb_item ON tra_cre_irb(item);
CREATE INDEX idx_tra_cre_sta_lei_period ON tra_cre_sta(lei_code, period);  
CREATE INDEX idx_tra_oth_lei_period ON tra_oth(lei_code, period);

-- Business key lookups
CREATE INDEX idx_list_of_banks_lei ON list_of_banks(lei_code);
CREATE INDEX idx_sdd_item ON sdd(item);
```

**Dimensional Analysis Indexes:**
```sql
CREATE INDEX idx_tra_cre_irb_scenario ON tra_cre_irb(scenario);
CREATE INDEX idx_tra_cre_irb_country ON tra_cre_irb(country_code);
CREATE INDEX idx_tra_cre_irb_portfolio ON tra_cre_irb(portfolio);
```

This enhanced relationship documentation shows exactly how all tables connect, what the primary and foreign keys are, and how to properly join data for analysis.

## Business Context

### Stress Testing Framework

**Scenarios:**
- **Actual (1)**: Historical performance data
- **Baseline (2)**: ECB's baseline economic scenario
- **Adverse (3)**: Severe but plausible stress scenario

### Credit Risk Approaches

**IRB (Internal Ratings Based):**
- Banks use internal models to calculate risk parameters
- Foundation IRB: Banks estimate PD, supervisors set LGD/EAD
- Advanced IRB: Banks estimate PD, LGD, EAD, M

**Standardized Approach:**
- Banks use standardized risk weights set by regulators
- Simpler approach for smaller or less sophisticated banks

### IFRS9 Stages

**Stage 1**: Performing assets (12-month ECL)
**Stage 2**: Significant increase in credit risk (lifetime ECL)
**Stage 3**: Credit-impaired assets (lifetime ECL)

## Data Usage Examples

### Common Queries

**Bank Summary by Country:**
```sql
SELECT 
    c.label as country_name,
    COUNT(*) as num_banks,
    AVG(t.amount) as avg_amount
FROM tra_oth t
JOIN country c ON t.country = c.country
JOIN sdd s ON t.item = s.item
WHERE s.label LIKE '%Capital%'
GROUP BY c.country, c.label;
```

**Credit Risk by Portfolio Type:**
```sql
SELECT 
    p.label as portfolio_type,
    SUM(t.amount) as total_amount
FROM tra_cre_irb t
JOIN portfolio p ON t.portfolio = p.portfolio
WHERE t.scenario = 3  -- Adverse scenario
GROUP BY p.portfolio, p.label
ORDER BY total_amount DESC;
```

**IFRS9 Distribution:**
```sql
SELECT 
    i.label as ifrs9_stage,
    ps.label as performance_status,
    COUNT(*) as records,
    SUM(t.amount) as total_exposure
FROM tra_cre_irb t
JOIN ifrs9_stages i ON t.ifrs9_stages = i.ifrs9_stages
JOIN perf_status ps ON t.perf_status = ps.perf_status
GROUP BY i.ifrs9_stages, i.label, ps.perf_status, ps.label;
```

## Data Quality Notes

**Amount Fields:**
- All amounts in millions EUR
- Negative values represent losses/impairments
- Zero values indicate no exposure/activity
- Scale can range from cents to billions

**Temporal Data:**
- Primary period: 202412 (December 2024)
- Historical comparisons available
- Some items may have earlier periods (201801, etc.)

**Coverage:**
- Major European banks under ECB supervision
- Not all banks report all metrics
- Some specialization by bank type and jurisdiction

## Performance Optimization

**Recommended Indexes:**
- `tra_cre_irb(lei_code, period, item)`
- `tra_cre_sta(lei_code, period, item)`  
- `tra_oth(lei_code, period, item)`
- `list_of_banks(lei_code)`

**Query Patterns:**
- Bank-specific analysis: Filter by `lei_code`
- Time series: Filter by `period`
- Metric analysis: Join with `sdd` on `item`
- Geographic analysis: Join with `country`
- Scenario comparison: Filter by `scenario`

This documentation provides the foundation for understanding and effectively using the EBA Transparency Exercise 2025 database for regulatory analysis, risk assessment, and financial research.
