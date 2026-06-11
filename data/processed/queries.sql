-- ============================================================================
-- ANALYTICAL SQL QUERIES - BLUESTOCK MUTUAL FUND ANALYSIS
-- ============================================================================

-- Q1: Top 5 Funds by Assets Under Management (AUM)
-- Purpose: Identify the largest funds by AUM and their performance

-- Q1_Top_5_Funds_by_AUM

SELECT 
    df.scheme_name,
    df.fund_house,
    df.category,
    fp.aum_crore,
    fp.return_1yr_pct,
    fp.expense_ratio_pct
FROM fact_performance fp
JOIN dim_fund df ON fp.fund_id = df.fund_id
ORDER BY fp.aum_crore DESC
LIMIT 5;


-- Q2_Average_NAV_by_Month

SELECT 
    dd.year,
    dd.month,
    df.scheme_name,
    ROUND(AVG(fn.nav), 4) as avg_nav,
    ROUND(MIN(fn.nav), 4) as min_nav,
    ROUND(MAX(fn.nav), 4) as max_nav,
    COUNT(*) as trading_days
FROM fact_nav fn
JOIN dim_fund df ON fn.fund_id = df.fund_id
JOIN dim_date dd ON fn.date_id = dd.date_id
GROUP BY dd.year, dd.month, df.scheme_name
ORDER BY dd.year DESC, dd.month DESC
LIMIT 20;


-- Q3_SIP_vs_Lumpsum_Growth

SELECT 
    ft.transaction_type as investment_type,
    COUNT(*) as transaction_count,
    SUM(ft.amount_inr) as total_amount,
    ROUND(AVG(ft.amount_inr), 2) as avg_transaction,
    COUNT(DISTINCT ft.investor_id) as unique_investors
FROM fact_transactions ft
GROUP BY ft.transaction_type
ORDER BY total_amount DESC;


-- Q4_Transactions_by_State

SELECT 
    ft.state,
    COUNT(*) as transaction_count,
    SUM(ft.amount_inr) as total_amount,
    COUNT(DISTINCT ft.investor_id) as unique_investors,
    ROUND(AVG(ft.amount_inr), 2) as avg_amount
FROM fact_transactions ft
GROUP BY ft.state
ORDER BY total_amount DESC
LIMIT 10;


-- Q5_Funds_with_Expense_Ratio_Below_1pct

SELECT 
    df.scheme_name,
    df.fund_house,
    df.category,
    fp.expense_ratio_pct,
    fp.return_3yr_pct,
    fp.aum_crore,
    fp.morningstar_rating
FROM fact_performance fp
JOIN dim_fund df ON fp.fund_id = df.fund_id
WHERE fp.expense_ratio_pct < 1.0
ORDER BY fp.return_3yr_pct DESC;


-- Q6_YoY_SIP_Growth

SELECT 
    dd.year,
    COUNT(*) as sip_transactions,
    SUM(ft.amount_inr) as total_sip_amount,
    COUNT(DISTINCT ft.investor_id) as unique_sip_investors,
    ROUND(AVG(ft.amount_inr), 2) as avg_sip_amount
FROM fact_transactions ft
JOIN dim_date dd ON ft.date_id = dd.date_id
WHERE ft.transaction_type = 'SIP'
GROUP BY dd.year
ORDER BY dd.year DESC;


-- Q7_Demographics_by_Age_Group

SELECT 
    ft.age_group,
    COUNT(DISTINCT ft.investor_id) as unique_investors,
    COUNT(*) as transactions,
    SUM(ft.amount_inr) as total_invested,
    ROUND(AVG(ft.amount_inr), 2) as avg_investment,
    ROUND(AVG(ft.annual_income_lakh), 2) as avg_annual_income_lakh
FROM fact_transactions ft
WHERE ft.kyc_status = 'Verified'
GROUP BY ft.age_group
ORDER BY total_invested DESC;


-- Q8_Performance_Metrics_by_Category

SELECT 
    df.category,
    COUNT(*) as fund_count,
    ROUND(AVG(fp.return_1yr_pct), 2) as avg_return_1yr,
    ROUND(AVG(fp.return_3yr_pct), 2) as avg_return_3yr,
    ROUND(AVG(fp.return_5yr_pct), 2) as avg_return_5yr,
    ROUND(AVG(fp.sharpe_ratio), 2) as avg_sharpe,
    ROUND(AVG(fp.max_drawdown_pct), 2) as avg_max_drawdown
FROM fact_performance fp
JOIN dim_fund df ON fp.fund_id = df.fund_id
GROUP BY df.category
ORDER BY avg_return_3yr DESC;


-- Q9_Redemptions_Analysis

SELECT 
    df.scheme_name,
    df.fund_house,
    COUNT(*) as redemption_count,
    SUM(ft.amount_inr) as total_redeemed,
    ROUND(AVG(ft.amount_inr), 2) as avg_redemption_amount
FROM fact_transactions ft
JOIN dim_fund df ON ft.fund_id = df.fund_id
WHERE ft.transaction_type = 'REDEMPTION'
GROUP BY df.scheme_name, df.fund_house
ORDER BY total_redeemed DESC
LIMIT 10;


-- Q10_Payment_Mode_Preferences

SELECT 
    ft.payment_mode,
    COUNT(*) as transaction_count,
    SUM(ft.amount_inr) as total_amount,
    ROUND(AVG(ft.amount_inr), 2) as avg_amount,
    COUNT(DISTINCT ft.investor_id) as unique_investors,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM fact_transactions), 2) as pct_of_all_transactions
FROM fact_transactions ft
GROUP BY ft.payment_mode
ORDER BY total_amount DESC;

