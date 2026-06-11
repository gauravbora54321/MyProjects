# Data Dictionary - Bluestock Mutual Fund Analysis

## Overview
This data dictionary documents all tables, columns, data types, and business definitions for the Bluestock mutual fund analytics database.

---

## DIMENSION TABLES

### dim_date
Time dimension for temporal analysis.

| Column | Type | Description |
|--------|------|-------------|
| date_id | INTEGER (PK) | Unique identifier for each date |
| date | DATE | Calendar date (YYYY-MM-DD) |
| year | INTEGER | Calendar year |
| month | INTEGER | Month of year (1-12) |
| day | INTEGER | Day of month (1-31) |
| quarter | INTEGER | Quarter (1-4) |
| day_of_week | TEXT | Day name (Monday-Sunday) |
| is_weekend | INTEGER | 1 if Saturday/Sunday, 0 otherwise |
| is_holiday | INTEGER | 1 if Indian holiday, 0 otherwise |

### dim_fund
Mutual fund scheme dimension.

| Column | Type | Description |
|--------|------|-------------|
| fund_id | INTEGER (PK) | Unique fund identifier |
| amfi_code | INTEGER (UK) | AMFI registration code |
| scheme_name | TEXT | Official scheme name |
| fund_house | TEXT | Mutual fund company (e.g., SBI, ICICI, Axis) |
| category | TEXT | Fund category (Large Cap, Mid Cap, Small Cap, Debt, etc.) |
| plan | TEXT | Plan type (Regular or Direct) |

---

## FACT TABLES

### fact_nav
Net Asset Value (NAV) history for each fund.

| Column | Type | Description |
|--------|------|-------------|
| nav_id | INTEGER (PK) | Unique NAV record identifier |
| fund_id | INTEGER (FK) | Reference to dim_fund |
| date_id | INTEGER (FK) | Reference to dim_date |
| nav | DECIMAL(10,4) | Net Asset Value per unit (Rs) |

**Business Rules:**
- NAV must be > 0
- One NAV per fund per trading day
- Forward-filled for holidays/weekends

### fact_transactions
Investor transactions (SIP, Lumpsum, Redemption).

| Column | Type | Description |
|--------|------|-------------|
| transaction_id | INTEGER (PK) | Unique transaction identifier |
| investor_id | TEXT | Unique investor identifier |
| fund_id | INTEGER (FK) | Reference to dim_fund |
| date_id | INTEGER (FK) | Reference to dim_date |
| transaction_type | TEXT | SIP, LUMPSUM, or REDEMPTION |
| amount_inr | DECIMAL(15,2) | Transaction amount in Indian Rupees |
| state | TEXT | Investor's state |
| city | TEXT | Investor's city |
| city_tier | TEXT | City tier (T30, B30, etc.) |
| age_group | TEXT | Age bracket (18-25, 26-35, 36-45, 46-55, 56+) |
| gender | TEXT | Male or Female |
| annual_income_lakh | DECIMAL(10,2) | Annual income in lakhs (Rs 100,000s) |
| payment_mode | TEXT | UPI, Cheque, Mandate, etc. |
| kyc_status | TEXT | Verified, Pending, or Rejected |

**Business Rules:**
- Amount must be > 0
- Transaction type must be one of: SIP, LUMPSUM, REDEMPTION
- KYC status must be: Verified, Pending, or Rejected

### fact_performance
Fund performance metrics and risk indicators.

| Column | Type | Description |
|--------|------|-------------|
| performance_id | INTEGER (PK) | Unique performance record |
| fund_id | INTEGER (FK, UK) | Reference to dim_fund (one per fund) |
| return_1yr_pct | DECIMAL(8,2) | 1-year return (%) |
| return_3yr_pct | DECIMAL(8,2) | 3-year CAGR (%) |
| return_5yr_pct | DECIMAL(8,2) | 5-year CAGR (%) |
| benchmark_3yr_pct | DECIMAL(8,2) | Benchmark 3-year return (%) |
| alpha | DECIMAL(8,2) | Jensen's alpha vs. benchmark |
| beta | DECIMAL(8,2) | Fund beta (volatility measure) |
| sharpe_ratio | DECIMAL(8,2) | Return per unit of risk |
| sortino_ratio | DECIMAL(8,2) | Return per unit of downside risk |
| std_dev_ann_pct | DECIMAL(8,2) | Annual standard deviation (%) |
| max_drawdown_pct | DECIMAL(8,2) | Maximum peak-to-trough decline (%) |
| aum_crore | DECIMAL(15,2) | Assets Under Management (Rs crores) |
| expense_ratio_pct | DECIMAL(8,2) | Annual expense ratio (%) |
| morningstar_rating | INTEGER | Morningstar rating (1-5 stars) |
| risk_grade | TEXT | Risk classification (Low, Moderate, High, Very High) |

**Business Rules:**
- Expense ratio must be between 0.1% and 2.5%
- One performance record per fund
- All return values should be numeric

---

## KEY METRICS & DEFINITIONS

### Transaction Types
- **SIP (Systematic Investment Plan):** Regular monthly/quarterly investments
- **LUMPSUM:** One-time investment
- **REDEMPTION:** Withdrawal of invested amount

### Performance Ratios
- **Sharpe Ratio:** Higher is better (measures risk-adjusted returns)
- **Beta:** <1 = less volatile than market, >1 = more volatile
- **Alpha:** Excess return above benchmark (positive is outperformance)
- **Sortino Ratio:** Similar to Sharpe but penalizes downside volatility

### Data Quality Rules Applied
1. Duplicate transactions removed
2. Missing NAVs forward-filled for holidays
3. Invalid transaction types filtered (only SIP/LUMPSUM/REDEMPTION)
4. Negative amounts removed
5. KYC status validated against enum values
6. Expense ratios validated within 0.1% - 2.5% range

---

## DATA SOURCES

| Table | Source | Format | Row Count |
|-------|--------|--------|-----------|
| dim_fund, fact_performance | scheme_performance.csv | CSV | 40 funds |
| fact_nav | nav_history.csv | CSV | 46,000 NAV records |
| fact_transactions | investor_transactions.csv | CSV | 32,778 transactions |

---

## UPDATED: 2024
