import pandas as pd
import numpy as np
import os
import json
from pathlib import Path

print("=" * 80)
print("DATA INGESTION PIPELINE - DAY 1")
print("=" * 80)

# Create necessary directories
paths = {
    'raw': 'data/raw',
    'processed': 'data/processed',
    'notebooks': 'notebooks',
    'sql': 'sql',
    'dashboard': 'dashboard',
    'reports': 'reports'
}

for path in paths.values():
    Path(path).mkdir(parents=True, exist_ok=True)

# ============================================================================
# STEP 1: Load all 10 CSV datasets
# ============================================================================
print("\n[STEP 1] Loading CSV Datasets")
print("-" * 80)

csv_files = [
    'fund_master.csv',
    'nav_history.csv',
    'scheme_details.csv',
    'performance_data.csv',
    'risk_metrics.csv',
    'holdings_data.csv',
    'expense_ratio.csv',
    'daily_returns.csv',
    'market_data.csv',
    'benchmark_data.csv'
]

datasets = {}
data_quality_issues = []

for csv_file in csv_files:
    file_path = f'{paths["raw"]}/{csv_file}'
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"⚠️  {csv_file}: FILE NOT FOUND - will be created after API fetch")
        continue
    
    try:
        df = pd.read_csv(file_path)
        datasets[csv_file] = df
        
        print(f"\n✓ {csv_file}")
        print(f"  Shape: {df.shape}")
        print(f"  Data Types:\n{df.dtypes.to_string()}")
        print(f"  First 5 rows:")
        print(df.head().to_string())
        
        # Check for anomalies
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            print(f"  ⚠️  Missing Values: {dict(null_counts[null_counts > 0])}")
            data_quality_issues.append(f"{csv_file}: Contains {null_counts.sum()} missing values")
        
        duplicate_rows = df.duplicated().sum()
        if duplicate_rows > 0:
            print(f"  ⚠️  Duplicate Rows: {duplicate_rows}")
            data_quality_issues.append(f"{csv_file}: Contains {duplicate_rows} duplicate rows")
            
    except Exception as e:
        print(f"✗ {csv_file}: Error loading - {str(e)}")
        data_quality_issues.append(f"{csv_file}: Failed to load - {str(e)}")

# ============================================================================
# STEP 2: Fetch Live NAV from mfapi.in
# ============================================================================
print("\n\n[STEP 2] Fetching Live NAV Data from mfapi.in")
print("-" * 80)

import requests

nav_schemes = {
    'HDFC Top 100 Direct': '125497',
    'SBI Bluechip': '119551',
    'ICICI Bluechip': '120503',
    'Nippon Large Cap': '118632',
    'Axis Bluechip': '119092',
    'Kotak Bluechip': '120841'
}

nav_data_list = []

for scheme_name, scheme_code in nav_schemes.items():
    try:
        url = f'https://api.mfapi.in/mf/{scheme_code}'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            meta = data.get('meta', {})
            nav_history = data.get('data', [])
            
            print(f"\n✓ {scheme_name} (Code: {scheme_code})")
            print(f"  Scheme Name: {meta.get('scheme_name', 'N/A')}")
            print(f"  ISIN: {meta.get('isin', 'N/A')}")
            print(f"  NAV Records: {len(nav_history)}")
            
            if nav_history:
                latest = nav_history[0]
                print(f"  Latest NAV: ₹{latest.get('nav', 'N/A')} ({latest.get('date', 'N/A')})")
            
            # Store for CSV export
            for record in nav_history:
                nav_data_list.append({
                    'scheme_code': scheme_code,
                    'scheme_name': scheme_name,
                    'date': record.get('date'),
                    'nav': record.get('nav'),
                    'isin': meta.get('isin')
                })
        else:
            print(f"✗ {scheme_name}: API Error - Status {response.status_code}")
            data_quality_issues.append(f"{scheme_name}: API fetch failed - Status {response.status_code}")
            
    except Exception as e:
        print(f"✗ {scheme_name}: {str(e)}")
        data_quality_issues.append(f"{scheme_name}: Fetch error - {str(e)}")

# Save NAV data to CSV
if nav_data_list:
    nav_df = pd.DataFrame(nav_data_list)
    nav_csv_path = f'{paths["raw"]}/live_nav_fetch.csv'
    nav_df.to_csv(nav_csv_path, index=False)
    print(f"\n✓ Live NAV data saved: {nav_csv_path} ({len(nav_df)} records)")
    datasets['live_nav_fetch.csv'] = nav_df

# ============================================================================
# STEP 3: Fund Master Exploration
# ============================================================================
print("\n\n[STEP 3] Fund Master Exploration")
print("-" * 80)

if 'fund_master.csv' in datasets:
    fm = datasets['fund_master.csv']
    
    print(f"\nFund Master Dataset: {fm.shape}")
    print(f"Columns: {list(fm.columns)}")
    
    print(f"\nUnique Fund Houses: {fm['Fund_House'].nunique() if 'Fund_House' in fm.columns else 'N/A'}")
    if 'Fund_House' in fm.columns:
        print(f"  {fm['Fund_House'].unique()[:10]}")
    
    print(f"\nUnique Categories: {fm['Category'].nunique() if 'Category' in fm.columns else 'N/A'}")
    if 'Category' in fm.columns:
        print(f"  {fm['Category'].unique()}")
    
    print(f"\nUnique Sub-Categories: {fm['Sub_Category'].nunique() if 'Sub_Category' in fm.columns else 'N/A'}")
    if 'Sub_Category' in fm.columns:
        print(f"  {fm['Sub_Category'].unique()[:10]}")
    
    print(f"\nUnique Risk Grades: {fm['Risk_Grade'].nunique() if 'Risk_Grade' in fm.columns else 'N/A'}")
    if 'Risk_Grade' in fm.columns:
        print(f"  {fm['Risk_Grade'].unique()}")
    
    print(f"\nAMFI Scheme Code Structure:")
    if 'Scheme_Code' in fm.columns:
        sample_codes = fm['Scheme_Code'].head(10).tolist()
        print(f"  Sample codes: {sample_codes}")
        print(f"  Code range: {fm['Scheme_Code'].min()} to {fm['Scheme_Code'].max()}")
else:
    print("⚠️  fund_master.csv not found in data/raw/")

# ============================================================================
# STEP 4: AMFI Code Validation
# ============================================================================
print("\n\n[STEP 4] AMFI Code Validation")
print("-" * 80)

if 'fund_master.csv' in datasets and 'nav_history.csv' in datasets:
    fm = datasets['fund_master.csv']
    nh = datasets['nav_history.csv']
    
    fm_codes = set(fm['Scheme_Code'].unique()) if 'Scheme_Code' in fm.columns else set()
    nh_codes = set(nh['Scheme_Code'].unique()) if 'Scheme_Code' in nh.columns else set()
    
    if fm_codes and nh_codes:
        missing_in_nav = fm_codes - nh_codes
        extra_in_nav = nh_codes - fm_codes
        
        print(f"Fund Master Schemes: {len(fm_codes)}")
        print(f"NAV History Schemes: {len(nh_codes)}")
        print(f"Missing in NAV History: {len(missing_in_nav)}")
        print(f"Extra in NAV History: {len(extra_in_nav)}")
        
        if missing_in_nav:
            print(f"  Sample missing: {list(missing_in_nav)[:5]}")
            data_quality_issues.append(f"{len(missing_in_nav)} schemes missing from nav_history")
    else:
        print("⚠️  Could not validate - Scheme_Code column not found")
else:
    print("⚠️  Both datasets needed for validation")

# ============================================================================
# DATA QUALITY SUMMARY
# ============================================================================
print("\n\n[DATA QUALITY SUMMARY]")
print("=" * 80)

if data_quality_issues:
    print(f"Issues Found: {len(data_quality_issues)}")
    for issue in data_quality_issues:
        print(f"  • {issue}")
else:
    print("✓ No critical data quality issues detected")

print(f"\nTotal Datasets Loaded: {len(datasets)}")
print(f"Files in data/raw/: {len(os.listdir(paths['raw']))}")

print("\n" + "=" * 80)
print("✓ DATA INGESTION COMPLETED SUCCESSFULLY")
print("=" * 80)
