import requests
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

print("=" * 80)
print("LIVE NAV FETCHER - Mutual Fund API Integration")
print("=" * 80)

# Ensure data directory exists
Path('data/raw').mkdir(parents=True, exist_ok=True)

# Define schemes to fetch
schemes = {
    'HDFC Top 100 Direct': '125497',
    'SBI Bluechip': '119551',
    'ICICI Bluechip': '120503',
    'Nippon Large Cap': '118632',
    'Axis Bluechip': '119092',
    'Kotak Bluechip': '120841'
}

all_nav_data = []
errors = []

print(f"\nFetching NAV data for {len(schemes)} schemes from mfapi.in...")
print("-" * 80)

for scheme_name, scheme_code in schemes.items():
    try:
        url = f'https://api.mfapi.in/mf/{scheme_code}'
        print(f"\n[{scheme_name}] Code: {scheme_code}")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        meta = data.get('meta', {})
        nav_records = data.get('data', [])
        
        # Extract metadata
        scheme_full_name = meta.get('scheme_name', 'N/A')
        isin = meta.get('isin', 'N/A')
        
        print(f"  ✓ Full Name: {scheme_full_name}")
        print(f"  ✓ ISIN: {isin}")
        print(f"  ✓ Records: {len(nav_records)}")
        
        if nav_records:
            latest = nav_records[0]
            print(f"  ✓ Latest NAV: ₹{latest.get('nav')} ({latest.get('date')})")
        
        # Process records
        for record in nav_records:
            all_nav_data.append({
                'scheme_code': scheme_code,
                'scheme_name': scheme_name,
                'full_name': scheme_full_name,
                'isin': isin,
                'date': record.get('date'),
                'nav': float(record.get('nav', 0)) if record.get('nav') else None,
                'fetch_timestamp': datetime.now().isoformat()
            })
        
        # Save individual scheme file
        scheme_df = pd.DataFrame([
            {
                'date': r.get('date'),
                'nav': float(r.get('nav', 0)) if r.get('nav') else None,
                'scheme_code': scheme_code
            }
            for r in nav_records
        ])
        
        safe_name = scheme_name.lower().replace(' ', '_')
        scheme_file = f'data/raw/nav_{safe_name}.csv'
        scheme_df.to_csv(scheme_file, index=False)
        print(f"  ✓ Saved: {scheme_file}")
        
    except requests.exceptions.RequestException as e:
        error_msg = f"{scheme_name} ({scheme_code}): {str(e)}"
        print(f"  ✗ {error_msg}")
        errors.append(error_msg)
    except Exception as e:
        error_msg = f"{scheme_name} ({scheme_code}): Unexpected error - {str(e)}"
        print(f"  ✗ {error_msg}")
        errors.append(error_msg)

# Save consolidated NAV file
print("\n" + "-" * 80)
if all_nav_data:
    nav_df = pd.DataFrame(all_nav_data)
    
    # Sort by date descending
    nav_df['date'] = pd.to_datetime(nav_df['date'])
    nav_df = nav_df.sort_values('date', ascending=False)
    
    output_file = 'data/raw/live_nav_consolidated.csv'
    nav_df.to_csv(output_file, index=False)
    
    print(f"\n✓ CONSOLIDATED NAV DATA")
    print(f"  File: {output_file}")
    print(f"  Total Records: {len(nav_df)}")
    print(f"  Unique Schemes: {nav_df['scheme_code'].nunique()}")
    print(f"  Date Range: {nav_df['date'].min()} to {nav_df['date'].max()}")
    print(f"\nData Preview:")
    print(nav_df.head(10).to_string())
else:
    print("✗ No NAV data could be fetched")

# Summary
print("\n" + "=" * 80)
if errors:
    print(f"⚠️  COMPLETED WITH {len(errors)} ERRORS:")
    for error in errors:
        print(f"  • {error}")
else:
    print("✓ ALL SCHEMES FETCHED SUCCESSFULLY")

print("=" * 80)
