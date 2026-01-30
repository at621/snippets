# Credit Risk Scorecard Pipeline
## Deep Feature Synthesis + Marginal Information Value

### Project Plan and Expected Outputs

---

## Source Attribution

This document distinguishes between information from the Revolut paper and implementation decisions made to fill gaps.

| Symbol | Meaning |
|--------|---------|
| 📄 | **From Revolut Paper** — Directly stated or shown in the paper/slides |
| 🔧 | **Implementation Decision** — My deduction to fill gaps not specified in paper |
| 📚 | **From Referenced Sources** — From papers/books cited by Revolut (Siddiqi, Scallan, etc.) |

---

## 1. Overview

This project implements Revolut's methodology for automated credit scorecard development as presented at the Edinburgh Credit Risk Conference (August 2025). The pipeline combines:

- 📄 **Deep Feature Synthesis (DFS)** for automated feature generation from relational data
- 📄 **Marginal Information Value (MIV)** for iterative feature selection
- 📄 **Weight of Evidence (WoE)** transformation for logistic regression compatibility
- 🔧 **Optimal Binning** via optbinning (paper mentions decision-tree based binning but not specific library)

### Reference Architecture (from Revolut Presentation)

📄 *This diagram is directly from the Revolut slides (Slide 3)*

```
┌─────────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────────┐
│   FEATURE GENERATION    │    │    FEATURE SELECTION    │    │   MODEL RECALIBRATION   │
├─────────────────────────┤    ├─────────────────────────┤    ├─────────────────────────┤
│                         │    │                         │    │                         │
│  ┌─────────────────┐    │    │  ┌─────────────────┐    │    │  ┌─────────────────┐    │
│  │ Data Collection │    │    │  │  Iterative MIV  │◄───┼────┼──│WoE Transformation│   │
│  └────────┬────────┘    │    │  │   Calculation   │    │    │  └────────┬────────┘    │
│           │             │    │  └────────▲────────┘    │    │           │             │
│           ▼             │    │           │             │    │           ▼             │
│  ┌─────────────────┐    │    │           │             │    │    ┌───────────┐        │
│  │Entity Set       │    │    │           │             │    │    │           │        │
│  │Creation         │    │    │           │             │    │    │  Final    │        │
│  └────────┬────────┘    │    │           │             │    │    │  Model    │        │
│           │             │    │           │             │    │    │           │        │
│           ▼             │    │           │             │    │    └───────────┘        │
│  ┌─────────────────┐    │    │  ┌────────┴────────┐    │    │                         │
│  │    Feature      │────┼────┼─►│ Information     │    │    │                         │
│  │   Generation    │    │    │  │ Value Calc      │    │    │                         │
│  └─────────────────┘    │    │  └─────────────────┘    │    │                         │
│                         │    │                         │    │                         │
└─────────────────────────┘    └─────────────────────────┘    └─────────────────────────┘
```

**Key Insight**: The process is recursive — features are added iteratively until model GINI on test set stops increasing.

---

## 2. Data Schema

### 2.1 Entities

🔧 *The paper mentions "transactional data", "credit bureau data", and "application usage data" but does not specify exact schema. This schema is my design based on typical digital bank data structures.*

We simulate a digital bank environment similar to Revolut with the following entities:

| Entity | Type | Description | Primary Key | Time Index |
|--------|------|-------------|-------------|------------|
| `customers` | 🔧 | Customer demographics and account info | `customer_id` | `signup_date` |
| `credit_applications` | 📄 | Loan/credit card applications (TARGET) | `application_id` | `application_date` |
| `transactions` | 📄 | Current account transactions | `transaction_id` | `transaction_date` |
| `credit_bureau` | 📄 | External credit bureau data | `bureau_id` | `inquiry_date` |

### 2.2 Relationships

🔧 *Relationships inferred from paper's DFS examples (Figure 4 shows employers → accounts → customers)*

```
customers (1) ────────► (N) credit_applications
    │
    │ (1)
    │
    └──────────────────► (N) transactions

credit_applications (1) ► (1) credit_bureau
```

### 2.3 Data Volumes

🔧 *Not specified in paper. These volumes chosen to be realistic for development/testing while remaining manageable.*

| Entity | Records | Notes |
|--------|---------|-------|
| `customers` | 50,000 | Unique customers |
| `credit_applications` | 80,000 | ~1.6 applications per customer average |
| `transactions` | 5,000,000 | ~100 transactions per customer average |
| `credit_bureau` | 80,000 | One per application |

### 2.4 Target Variable

📄 *From Paper Section 2.2.1-2.2.3 — Paper explicitly discusses bad definition vs definition of default, prediction horizon, and censoring.*

Following Revolut's methodology:

- 📄 **Bad Definition** (for rank-ordering): Early delinquency indicator (paper mentions "14 days past due at 3 months on book" for monitoring, "90 DPD" mentioned in slides)
- 📄 **Prediction Horizon**: Paper shows cumulative default curves up to 24+ months (Figure 3)
- 📄 **Censoring**: "Accounts that have been observed for less than the full prediction horizon are considered 'censored' and should be excluded"

🔧 *Specific choice of 90 DPD @ 12 months is my decision based on industry standard and paper's Figure 3*

Expected bad rate: ~5-8% (realistic for unsecured consumer credit)

---

## 3. Feature Generation with DFS

### 3.1 Feature Types (from Paper Section 2.2.4)

📄 *Directly from Paper Section 2.2.4 — "Features are generated at two levels: the entity level and the relational level"*

| Type | Name | Description | Example | Source |
|------|------|-------------|---------|--------|
| `efeat` | Entity Feature | Single-table transformation | `MONTH(application_date)` | 📄 Paper |
| `dfeat` | Direct Feature | Join from parent entity | `customer.income` on application | 📄 Paper |
| `rfeat` | Relational Feature | Aggregate from child entities | `SUM(transactions.amount)` per customer | 📄 Paper |

### 3.2 Aggregation Primitives

📄 *Paper Section 2.2.4 mentions "mathematical primitives (e.g., sum, average)" and Figure 4 shows COUNT*
📄 *Paper Example 2 (Slide 8) shows TREND as an aggregation function*

For numeric columns:
- 📄 `count`, `sum`, `mean` — explicitly mentioned in paper
- 🔧 `std`, `min`, `max`, `median` — standard aggregations, not explicitly mentioned
- 🔧 `skew`, `percent_true`, `num_unique` — common in Featuretools, not mentioned in paper
- 📄 `trend` — explicitly shown in paper Example 2

For temporal columns:
- 🔧 `time_since_first`, `time_since_last` — my addition based on credit risk domain knowledge

### 3.3 Transform Primitives

🔧 *Not explicitly listed in paper, but efeat definition implies transforms exist*

- `year`, `month`, `day`, `weekday`, `hour`
- `is_weekend`

### 3.4 WHERE Clause Filters

📄 *Paper Example 2 (Slide 8) explicitly shows WHERE clause filtering:*
```
customer.TREND(account_history.amount_past_due, last_updated_on 
               WHERE account_history.contract_type = 'Personal_Loan')
```

📄 *Paper's Figure 9 shows `WHERE budget_category = TRAVEL` as a real example*

| Filter | Description | Source |
|--------|-------------|--------|
| `category = 'TRAVEL'` | Travel spending | 📄 Figure 9 |
| `contract_type = 'Personal_Loan'` | Filter by loan type | 📄 Example 2 |
| 🔧 `category = 'SALARY'` | Income transactions | My addition |
| 🔧 `category = 'GAMBLING'` | Gambling spend | My addition |
| 🔧 `category = 'GROCERIES'` | Essential spend | My addition |
| 🔧 `amount > 0` / `amount < 0` | Credits/Debits | My addition |

### 3.5 Time Windows

🔧 *Paper does not specify time windows used. This is my design based on industry practice.*

Features calculated over multiple lookback periods:
- Last 7 days
- Last 30 days
- Last 90 days
- Last 180 days
- Last 365 days
- All time (before application)

### 3.6 Point-in-Time Correctness

📄 *From Slide 9: "Reconstruct extracted data to state of context_date"*

**Critical**: For each `credit_application`, only use data available BEFORE `application_date`.

🔧 *Featuretools handles this via `cutoff_time` parameter — implementation detail not in paper*

### 3.7 Expected Output: Feature Matrix

🔧 *Feature counts are my estimates based on:*
- *Number of entities and columns*
- *Number of primitives and time windows*
- *Paper mentions "large set of features generated by DFS" without specific numbers*

| Metric | Expected Value | Source |
|--------|----------------|--------|
| Number of raw features generated | 500 - 2,000 | 🔧 Estimate |
| Features after removing low-variance | 300 - 1,000 | 🔧 Estimate |
| Features after removing high-missing | 200 - 800 | 🔧 Estimate |

Sample features generated:
```
customer.MEAN(transactions.amount)
customer.STD(transactions.amount)
customer.COUNT(transactions)
customer.SUM(transactions.amount WHERE category = 'SALARY')
customer.COUNT(transactions WHERE category = 'GAMBLING')
customer.TREND(transactions.amount, transaction_date)
customer.MEAN(transactions.amount) - customer.MEAN(transactions.amount WHERE last_30_days)
credit_bureau.num_inquiries_last_6m
credit_bureau.total_outstanding_balance
credit_bureau.worst_delinquency_ever
```

---

## 4. Feature Selection with MIV

### 4.1 Information Value (IV)

📄 *Formula directly from Paper Section 2.3.2*

Measures univariate predictive power:

```
IV(X) = Σ [(P(X=a|Bad) - P(X=a|Good)) × WoE_observed(X=a)]
```

📚 **IV Interpretation** *(from Siddiqi, cited in paper [2]):*
| IV Range | Predictive Power |
|----------|------------------|
| < 0.02 | Not useful |
| 0.02 - 0.10 | Weak |
| 0.10 - 0.30 | Medium |
| 0.30 - 0.50 | Strong |
| > 0.50 | Suspicious (check overfitting) |

### 4.2 Marginal Information Value (MIV)

📄 *Formula directly from Paper Section 2.3.2*

Measures **incremental** predictive power given features already in the model:

```
MIV(X) = Σ [(P(X=a|Bad) - P(X=a|Good)) × (WoE_observed(X=a) - WoE_expected(X=a))]
```

📄 *"Where WoE_expected is calculated based on the current model's scores"*

### 4.3 MIV Selection Algorithm

📄 *Process described in Paper Section 2.3.2:*
> "The MIV process begins by selecting the feature with the highest individual Information Value (IV). In subsequent steps, the feature with the highest MIV is added."

📄 *Stopping criteria from paper:*
> "The process continues until model performance on a test set plateaus or the highest MIV falls below a set threshold (e.g. 2%). A pairwise Pearson correlation threshold (e.g. 40%-60%) is also applied."

```
1. Initialize: selected_features = []                          📄 Paper
2. Calculate IV for all candidate features                     📄 Paper
3. Select feature with highest IV → add to selected_features   📄 Paper
4. Loop:
   a. Train logistic regression on WoE-transformed features    📄 Paper (implied)
   b. For each remaining candidate feature:
      - Calculate WoE_expected from model predictions          📄 Paper
      - Calculate MIV                                          📄 Paper
   c. Select feature with highest MIV                          📄 Paper
   d. Check stopping criteria:                                 📄 Paper
      - MIV < threshold (e.g., 0.02)                          📄 Paper (2%)
      - Test GINI not improving for N rounds                   📄 Paper
      - Correlation with existing features > threshold         📄 Paper (40-60%)
      - Max features reached                                   🔧 My addition
   e. If not stopped, add feature to selected_features
5. Return selected_features
```

### 4.4 Expected Output: Selected Features

| Metric | Expected Value | Source |
|--------|----------------|--------|
| Features input to MIV | 200 - 800 | 🔧 Estimate |
| Features selected | 10 - 25 | 🔧 Estimate based on Figure 5 showing ~16 steps |
| Total IV of selected features | 1.5 - 4.0 | 🔧 Estimate |
| Correlation between features | < 0.6 | 📄 Paper mentions 40-60% threshold |

📄 *Selection curve structure from Figure 5 in paper (ROC AUC vs step, MIV values per step):*
```
Step  Feature Added                                    MIV    Cumulative GINI
────  ─────────────────────────────────────────────   ─────  ───────────────
  1   (highest IV feature)                            ~0.8   ~0.45
  2   (second feature)                                ~0.4   ~0.52
  ...
 15   (diminishing returns)                           ~0.05  ~0.68
 16   (below threshold)                               ~0.03  ~0.68  ← stopping
```

🔧 *Specific feature names in the table above are my examples; paper doesn't list actual feature names selected*

---

## 5. Binning and WoE Transformation

### 5.1 Optimal Binning

📄 *Paper Section 2.2.5 describes the binning approach:*
> "A decision-tree-based approach is used to split the numeric part of a feature, minimising Gini impurity within each bin while ensuring each bin contains a minimum percentage (e.g., 5%) of observations."

📄 *Paper also mentions:*
> "Subsequently, bins with similar bad rates or insufficient observations are merged based on statistical tests (e.g., bootstrapped Z-test, Chi-square test, etc.)"

🔧 *Using optbinning library — paper doesn't specify library, but optbinning implements this methodology*

For each selected feature:
1. 📄 Pre-bin using decision tree (Gini-based splitting)
2. 📄 Merge bins ensuring:
   - 📄 Minimum 5% of observations per bin
   - 📚 Monotonic WoE trend (from Siddiqi)
   - 📄 Statistical significance between adjacent bins
3. 🔧 Output: 3-10 final bins per feature (my estimate)

### 5.2 WoE Transformation

📄 *Formula from Paper Section 2.2.6:*

```
WoE(X=a) = log(P(X=a|Bad) / P(X=a|Good))
```

📄 *Paper's interpretation:*
> "Positive WoE indicates that the proportion of bads is higher than the proportion of goods in that category, which indicates higher than average risk"

🔧 *Note: optbinning uses opposite sign convention (Good/Bad). Will need to handle in implementation.*

### 5.3 Expected Output: Binning Tables

🔧 *Sample table structure based on optbinning output format; specific values are illustrative*

Sample binning table for `credit_bureau.worst_delinquency`:

| Bin | Range | Count | Count % | Bad | Bad Rate | WoE | IV |
|-----|-------|-------|---------|-----|----------|-----|-----|
| 0 | Never delinquent | 45,000 | 56.3% | 1,200 | 2.7% | 0.82 | 0.31 |
| 1 | 1-29 DPD | 18,000 | 22.5% | 1,100 | 6.1% | -0.15 | 0.01 |
| 2 | 30-59 DPD | 10,000 | 12.5% | 900 | 9.0% | -0.58 | 0.05 |
| 3 | 60-89 DPD | 4,500 | 5.6% | 600 | 13.3% | -1.02 | 0.07 |
| 4 | 90+ DPD | 2,500 | 3.1% | 700 | 28.0% | -1.89 | 0.14 |
| **Total** | | **80,000** | **100%** | **4,500** | **5.6%** | | **0.58** |

---

## 6. Model Training

### 6.1 Scorecard Model

📄 *Paper Section 2.4.2:*
> "The MIV feature selection technique is theoretically related to logistic regression, and benchmarking shows that this combination frequently performs in line with, or better than, more complex models like tree ensembles."

📄 *Table 1 in paper shows Logistic Regression was chosen over Tree Ensemble in 4 out of 5 models*

- 📄 **Algorithm**: Logistic Regression
- 📄 **Input**: WoE-transformed selected features
- 📄 **Output**: Log-odds score

### 6.2 Scaling

📄 *Paper Section 2.4.1 mentions "Platt Scaling" for calibration*

🔧 *PDO-Odds scaling method from optbinning; paper doesn't specify exact scaling approach for scorecard points*

Transform log-odds to traditional scorecard points:

**PDO-Odds method:**
```
Score = Offset + Factor × log(odds)

Where:
- Offset = Target score at target odds
- Factor = PDO / log(2)
- PDO = Points to Double the Odds (typically 20)
```

🔧 **Example scaling** *(my choice of parameters):*
- Target: Score of 600 at odds of 50:1 (2% bad rate)
- PDO: 20 points

### 6.3 Expected Output: Model Performance

📄 *Paper Section 2.4.1 states:*
> "A good credit scoring model is expected to have a Gini value of at least 50%, although this can vary depending on the risk spectrum of the population."

📄 *Paper Table 1 shows actual GINI values from Revolut models:*
| Model | Tree Ensemble GINI | Logistic Regression GINI |
|-------|-------------------|-------------------------|
| Personal Loans A | 54% | 58% |
| Credit Cards A | 63% | 63% |
| Personal Loans B | 64% | 65% |
| Credit Cards B | 70% | 70% |
| Alternative Data Model | 55% | 43% |

🔧 *Expected ranges for our synthetic data (estimates):*

| Metric | Development | Test | Out-of-Time | Source |
|--------|-------------|------|-------------|--------|
| GINI | 0.60 - 0.70 | 0.55 - 0.65 | 0.50 - 0.60 | 🔧 Estimate |
| AUC | 0.80 - 0.85 | 0.77 - 0.82 | 0.75 - 0.80 | 🔧 Estimate |
| KS | 0.40 - 0.50 | 0.38 - 0.48 | 0.35 - 0.45 | 🔧 Estimate |

### 6.4 Expected Output: Scorecard Table

🔧 *Format based on optbinning Scorecard output; specific values illustrative*

| Variable | Bin | Points |
|----------|-----|--------|
| credit_bureau.worst_delinquency | Never delinquent | 45 |
| | 1-29 DPD | 32 |
| | 30-59 DPD | 24 |
| | 60-89 DPD | 15 |
| | 90+ DPD | 0 |
| customer.MEAN(transactions.amount WHERE SALARY) | < 1,000 | 0 |
| | 1,000 - 2,500 | 18 |
| | 2,500 - 4,000 | 28 |
| | > 4,000 | 38 |
| ... | ... | ... |
| **Base Score** | | 250 |
| **Score Range** | | 300 - 850 |

---

## 7. Pipeline Architecture

🔧 *This entire section is my implementation design. The paper describes the methodology but not the code structure.*

📄 *However, the high-level flow matches the paper's Figure 1:*
> Feature Generation → Feature Selection → Model Training and Benchmarking → Final Model

### 7.1 Directory Structure

```
credit_risk_pipeline/
├── README.md
├── PLAN.md                          ◄── This document
├── requirements.txt
├── pyproject.toml
│
├── src/
│   └── credit_risk/
│       ├── __init__.py
│       │
│       ├── data/
│       │   ├── __init__.py
│       │   ├── schema.py            # Entity definitions
│       │   ├── generator.py         # Synthetic data generator
│       │   └── loader.py            # Data loading utilities
│       │
│       ├── dfs/
│       │   ├── __init__.py
│       │   ├── entityset.py         # Featuretools EntitySet builder
│       │   ├── primitives.py        # Custom primitives (TREND, etc.)
│       │   └── synthesis.py         # DFS execution wrapper
│       │
│       ├── selection/
│       │   ├── __init__.py
│       │   ├── iv.py                # Information Value calculation
│       │   └── miv.py               # Marginal Information Value selection
│       │
│       ├── model/
│       │   ├── __init__.py
│       │   ├── scorecard.py         # Scorecard wrapper around optbinning
│       │   └── evaluation.py        # GINI, KS, calibration plots
│       │
│       └── pipeline/
│           ├── __init__.py
│           └── full_pipeline.py     # End-to-end orchestration
│
├── examples/
│   ├── 01_generate_data.py          # Create synthetic dataset
│   ├── 02_explore_data.py           # EDA and visualizations
│   ├── 03_run_dfs.py                # Feature generation
│   ├── 04_feature_selection.py      # IV/MIV selection
│   ├── 05_build_scorecard.py        # Final model
│   └── 06_full_pipeline.py          # End-to-end example
│
├── data/                            # Generated data (gitignored)
│   ├── raw/
│   │   ├── customers.parquet
│   │   ├── credit_applications.parquet
│   │   ├── transactions.parquet
│   │   └── credit_bureau.parquet
│   ├── processed/
│   │   └── feature_matrix.parquet
│   └── models/
│       ├── binning_process.pkl
│       └── scorecard.pkl
│
└── notebooks/
    └── walkthrough.ipynb            # Interactive demo
```

### 7.2 Module Responsibilities

| Module | Responsibility | Key Dependencies |
|--------|----------------|------------------|
| `data.generator` | Create realistic synthetic data | `numpy`, `pandas` |
| `dfs.synthesis` | Run DFS with Featuretools | `featuretools` |
| `selection.miv` | MIV-based feature selection | `optbinning`, `sklearn` |
| `model.scorecard` | Build and evaluate scorecard | `optbinning` |
| `pipeline.full_pipeline` | Orchestrate end-to-end | All above |

---

## 8. Synthetic Data Specification

🔧 *This entire section is my design. The paper does not provide data schemas or distributions.*

📄 *However, guided by paper's mentions of:*
- *"transactional data" (Slide 9, Section 4.1)*
- *"credit bureau data" (various)*
- *"alternative data sources not commonly used in credit risk management" (Section 4.1)*
- *"mobile app interactions" (Section 1.2.3)*
- *Transaction categories like "TRAVEL" (Figure 9)*

### 8.1 Customer Entity

🔧 *Schema designed to support DFS feature generation*

| Column | Type | Distribution | Description |
|--------|------|--------------|-------------|
| `customer_id` | str | UUID | Primary key |
| `signup_date` | datetime | 2020-01-01 to 2024-06-01 | Account opening date |
| `age` | int | Normal(35, 12), clipped 18-75 | Customer age |
| `income_annual` | float | LogNormal(10.5, 0.6) | Stated annual income |
| `employment_status` | str | Categorical | EMPLOYED/SELF_EMPLOYED/UNEMPLOYED/RETIRED |
| `housing_status` | str | Categorical | OWN/MORTGAGE/RENT |
| `region` | str | Categorical | Geographic region |

### 8.2 Credit Application Entity

| Column | Type | Distribution | Description |
|--------|------|--------------|-------------|
| `application_id` | str | UUID | Primary key |
| `customer_id` | str | FK | Foreign key to customer |
| `application_date` | datetime | signup_date + random | Application timestamp |
| `product_type` | str | Categorical | PERSONAL_LOAN/CREDIT_CARD |
| `requested_amount` | float | LogNormal | Amount requested |
| `loan_purpose` | str | Categorical | Purpose of loan |
| `bad_flag` | int | 0/1 | Target: 90+ DPD in 12 months |
| `months_on_book` | int | 0-24 | Observation period |

### 8.3 Transaction Entity

| Column | Type | Distribution | Description |
|--------|------|--------------|-------------|
| `transaction_id` | str | UUID | Primary key |
| `customer_id` | str | FK | Foreign key to customer |
| `transaction_date` | datetime | Random within account life | Transaction timestamp |
| `amount` | float | Mixed distribution | Transaction amount (+ credit, - debit) |
| `category` | str | Categorical | Transaction category |
| `merchant_name` | str | Categorical | Merchant identifier |
| `balance_after` | float | Running balance | Account balance after transaction |

Transaction categories:
- `SALARY` (income)
- `TRANSFER_IN`, `TRANSFER_OUT`
- `GROCERIES`, `RESTAURANTS`, `ENTERTAINMENT`
- `UTILITIES`, `RENT`, `MORTGAGE`
- `GAMBLING`, `ATM_WITHDRAWAL`
- `ONLINE_SHOPPING`, `TRAVEL`

### 8.4 Credit Bureau Entity

| Column | Type | Distribution | Description |
|--------|------|--------------|-------------|
| `bureau_id` | str | UUID | Primary key |
| `application_id` | str | FK | Foreign key to application |
| `inquiry_date` | datetime | = application_date | When bureau was pulled |
| `num_accounts` | int | Poisson(5) | Total credit accounts |
| `num_active_accounts` | int | ≤ num_accounts | Currently active accounts |
| `total_credit_limit` | float | LogNormal | Sum of all credit limits |
| `total_balance` | float | ≤ total_credit_limit | Current total balance |
| `utilization_ratio` | float | balance/limit | Credit utilization |
| `num_inquiries_6m` | int | Poisson(2) | Hard inquiries last 6 months |
| `worst_delinquency_ever` | str | Categorical | Worst historical delinquency |
| `months_since_delinquency` | int | Exponential | Months since last delinquency |
| `num_derogatory` | int | Poisson(0.5) | Derogatory marks |

### 8.5 Correlation with Target

🔧 *Correlation structure is my design to create realistic synthetic data*

📄 *Guided by paper's Figure 9 which shows travel spending correlates with lower delinquency*

To create realistic data, we introduce correlations between features and `bad_flag`:

| Feature | Direction | Strength | Source |
|---------|-----------|----------|--------|
| `worst_delinquency_ever` | Positive | Strong | 🔧 Standard credit risk |
| `utilization_ratio` | Positive | Strong | 🔧 Standard credit risk |
| `num_inquiries_6m` | Positive | Medium | 🔧 Standard credit risk |
| `income_annual` | Negative | Medium | 🔧 Standard credit risk |
| `age` | Negative (U-shape) | Weak | 🔧 Standard credit risk |
| `MEAN(transactions WHERE SALARY)` | Negative | Strong | 🔧 Logical inference |
| `STD(transactions.amount)` | Positive | Medium | 🔧 Income volatility |
| `COUNT(transactions WHERE GAMBLING)` | Positive | Medium | 🔧 Risk behavior |
| `SUM(transactions WHERE TRAVEL)` | Negative | Weak | 📄 Figure 9 shows this pattern |

---

## 9. Expected Outputs Summary

🔧 *All file sizes and specific outputs are my estimates based on the planned implementation*

### 9.1 Data Files

| File | Size (approx) | Records |
|------|---------------|---------|
| `customers.parquet` | 5 MB | 50,000 |
| `credit_applications.parquet` | 8 MB | 80,000 |
| `transactions.parquet` | 500 MB | 5,000,000 |
| `credit_bureau.parquet` | 10 MB | 80,000 |
| `feature_matrix.parquet` | 50 MB | 80,000 × 500 features |

### 9.2 Model Artifacts

| Artifact | Description |
|----------|-------------|
| `binning_process.pkl` | Fitted optbinning BinningProcess |
| `scorecard.pkl` | Fitted optbinning Scorecard |
| `feature_definitions.json` | Featuretools feature definitions |
| `selected_features.json` | MIV-selected feature list |
| `model_report.html` | Comprehensive model report |

### 9.3 Visualizations

📄 *Some visualizations match those shown in the paper:*

1. **Feature Generation**
   - 🔧 Entity relationship diagram
   - 🔧 Feature count by type (efeat/dfeat/rfeat)
   - 🔧 Missing value heatmap

2. **Feature Selection**
   - 🔧 IV distribution histogram
   - 📄 MIV selection curve (GINI vs. step) — *matches Figure 5*
   - 🔧 Feature correlation heatmap

3. **Model Performance**
   - 📄 ROC curve — *paper mentions AUC*
   - 📄 Lorenz curve (CAP) — *Figure 6 in paper*
   - 📄 KS statistic plot — *paper mentions KS*
   - 🔧 Score distribution by good/bad
   - 📄 Calibration plot — *Figure 7 in paper*

4. **Scorecard**
   - 🔧 Points distribution by variable
   - 🔧 Score-to-PD mapping curve

---

## 10. Usage Examples

🔧 *API design is entirely my implementation; paper does not provide code examples*

### 10.1 Quick Start

```python
from credit_risk.pipeline import CreditRiskPipeline

# Initialize pipeline
pipeline = CreditRiskPipeline(
    target_column='bad_flag',
    time_index='application_date',
    max_features=20,
    min_iv=0.02,
)

# Load data
pipeline.load_data(
    applications='data/raw/credit_applications.parquet',
    customers='data/raw/customers.parquet',
    transactions='data/raw/transactions.parquet',
    bureau='data/raw/credit_bureau.parquet',
)

# Run full pipeline
pipeline.run()

# Get results
scorecard = pipeline.get_scorecard()
report = pipeline.generate_report()
```

### 10.2 Step-by-Step

```python
# Step 1: Generate synthetic data
from credit_risk.data import generate_synthetic_data

data = generate_synthetic_data(
    n_customers=50_000,
    n_applications=80_000,
    n_transactions=5_000_000,
    bad_rate=0.06,
    seed=42,
)

# Step 2: Build EntitySet and run DFS
from credit_risk.dfs import build_entityset, run_dfs

es = build_entityset(data)
feature_matrix, feature_defs = run_dfs(
    entityset=es,
    target_entity='credit_applications',
    cutoff_time=data['applications'][['application_id', 'application_date']],
    max_depth=2,
)

# Step 3: Feature selection with MIV
from credit_risk.selection import MIVSelector

selector = MIVSelector(
    min_iv=0.02,
    max_features=20,
    correlation_threshold=0.6,
    early_stopping_rounds=3,
)
selected_features = selector.fit_select(
    X=feature_matrix,
    y=data['applications']['bad_flag'],
)

# Step 4: Build scorecard
from credit_risk.model import build_scorecard

scorecard = build_scorecard(
    X=feature_matrix[selected_features],
    y=data['applications']['bad_flag'],
    scaling_method='pdo_odds',
    scaling_params={'pdo': 20, 'score': 600, 'odds': 50},
)

# Step 5: Evaluate
from credit_risk.model import evaluate_scorecard

metrics = evaluate_scorecard(scorecard, X_test, y_test)
print(f"Test GINI: {metrics['gini']:.3f}")
print(f"Test KS: {metrics['ks']:.3f}")
```

---

## 11. Implementation Order

| Phase | Module | Description | Estimated Effort |
|-------|--------|-------------|------------------|
| 1 | `data.generator` | Synthetic data generation | Medium |
| 2 | `dfs.entityset` | Featuretools EntitySet builder | Low |
| 3 | `dfs.synthesis` | DFS wrapper with time windows | Medium |
| 4 | `selection.miv` | MIV calculation and selection | High |
| 5 | `model.scorecard` | optbinning scorecard wrapper | Low |
| 6 | `model.evaluation` | Performance metrics and plots | Medium |
| 7 | `pipeline.full_pipeline` | End-to-end orchestration | Medium |
| 8 | Examples and documentation | Usage examples | Low |

---

## 12. Validation Criteria

The implementation will be considered successful if:

1. **Data Generation** 🔧
   - [ ] All entities created with correct relationships
   - [ ] Bad rate within 5-8%
   - [ ] Realistic feature correlations with target

2. **Feature Generation (DFS)**
   - [ ] 500+ features generated 🔧
   - [ ] 📄 Point-in-time correctness verified (no leakage) — *paper emphasizes this*
   - [ ] 📄 All feature types represented (efeat, dfeat, rfeat)

3. **Feature Selection (MIV)**
   - [ ] 📄 MIV algorithm converges — *paper shows convergence in Figure 5*
   - [ ] 10-25 features selected 🔧
   - [ ] 📄 Selected features have low mutual correlation (<60%)

4. **Model Performance**
   - [ ] 📄 Test GINI > 0.50 — *paper states "at least 50%"*
   - [ ] Train-test GINI gap < 0.10 (no severe overfitting) 🔧
   - [ ] 📄 Monotonic WoE trends for all binned features — *paper Section 2.2.5*

5. **Scorecard**
   - [ ] 📄 All features have interpretable binning
   - [ ] Score range is reasonable (e.g., 300-850) 🔧
   - [ ] Score-to-PD mapping is monotonic 🔧

---

## 13. References

1. Kanter, J. & Veeramachaneni, K. (2015). Deep Feature Synthesis: Towards Automating Data Science Endeavors. IEEE DSAA.

2. Spinella, F. & Krisciunas, T. (2025). Enhancing Credit Risk Models at Revolut by Combining Deep Feature Synthesis and Marginal Information Value. Edinburgh Credit Risk Conference.

3. Navas-Palencia, G. (2020). Optimal Binning: Mathematical Programming Formulation. arXiv:2001.08025.

4. Siddiqi, N. (2017). Intelligent Credit Scoring: Building and Implementing Better Credit Risk Scorecards. Wiley.

5. Scallan, G. (2011). Class(ic) Scorecard: Selecting Characteristics and Attributes in Logistic Regression. Edinburgh Credit Scoring Conference.

---

## Appendix: Source Attribution Summary

### What Comes Directly From Revolut Paper 📄

| Component | Paper Reference |
|-----------|-----------------|
| Overall methodology (DFS + MIV + WoE + LogReg) | Figure 1, Section 2 |
| Feature types: efeat, dfeat, rfeat | Section 2.2.4 |
| TREND as aggregation primitive | Slide 8, Example 2 |
| WHERE clause filtering | Slide 8, Example 2; Figure 9 |
| Point-in-time data reconstruction | Slide 9 |
| Information Value formula | Section 2.3.2 |
| Marginal Information Value formula | Section 2.3.2 |
| MIV stopping criteria (2% threshold, 40-60% correlation) | Section 2.3.2 |
| Decision-tree based binning with 5% minimum | Section 2.2.5 |
| WoE formula and interpretation | Section 2.2.6 |
| Logistic regression as final model | Section 2.4.2, Table 1 |
| GINI ≥ 50% as quality threshold | Section 2.4.1 |
| Platt scaling for calibration | Section 2.4.1 |
| Lorenz curve for evaluation | Figure 6 |
| Calibration plot | Figure 7 |
| MIV convergence curve shape | Figure 5 |
| Travel spending correlates with lower risk | Figure 9 |

### What I Deduced or Designed 🔧

| Component | Rationale |
|-----------|-----------|
| Specific data schema (columns, types) | Paper mentions data sources but not schema |
| Data volumes (50K customers, 5M transactions) | Reasonable for development/testing |
| Most aggregation primitives (std, min, max, etc.) | Standard in Featuretools; paper only mentions "sum, average" |
| Transform primitives (year, month, weekday, etc.) | Implied by efeat definition |
| Time windows (7d, 30d, 90d, etc.) | Industry standard; not specified in paper |
| Transaction categories (SALARY, GAMBLING, etc.) | Only TRAVEL explicitly mentioned |
| Feature count estimates (500-2000) | Based on schema complexity |
| Selected feature count (10-25) | Inferred from Figure 5 showing ~16 steps |
| All code structure and API design | Paper is methodology, not implementation |
| optbinning as library choice | Paper mentions decision-tree binning but not library |
| Score scaling parameters (PDO=20, etc.) | Industry standard; not in paper |
| Synthetic data distributions | Created to produce realistic correlations |

### From Referenced Sources 📚

| Component | Source |
|-----------|--------|
| IV interpretation thresholds | Siddiqi (2017), cited as [2] |
| Monotonic WoE requirement | Siddiqi (2017) |
| Reject inference concepts | Banasik & Crook (2007), cited as [8] |
| Brier Score formula | Brier (1950), cited as [13] |
