import pandas as pd
import numpy as np
import os

# Configuration
directory = r'c:\Users\dlstj\OneDrive\Desktop\ICB6\Team_miniproject1'
output_report = os.path.join(directory, 'final_eda_report.md')

files = {
    'sales': '서울시_상권분석서비스(추정매출-상권)_2020-2025.csv',
    'store': '서울시_상권분석서비스(점포-상권)_20192025년.csv',
    'rent_small': '상권별_소규모_상가_임대가격지수_2020_2025.csv',
    'rent_medium': '상권별_중대형_상가_임대가격지수_2020_2025.csv'
}

def load_data(file_name):
    path = os.path.join(directory, file_name)
    # Common encodings for Korean public data
    for enc in ['cp949', 'utf-8-sig', 'utf-8']:
        try:
            df = pd.read_csv(path, encoding=enc)
            print(f"Loaded {file_name} with {enc}")
            return df
        except:
            continue
    return None

report_content = "# 📊 서울시 상권 분석 종합 EDA 리포트 (2020-2025)\n\n"

# 1. Sales Data Analysis
print("Analyzing Sales Data...")
df_sales = load_data(files['sales'])
if df_sales is not None:
    # Handle year filtering
    if '기준_년분기_코드' in df_sales.columns:
        df_sales['기준_년_코드'] = df_sales['기준_년분기_코드'] // 10
    
    if '기준_년_코드' in df_sales.columns:
        df_sales = df_sales[(df_sales['기준_년_코드'] >= 2020) & (df_sales['기준_년_코드'] <= 2025)]
    
    # Missing Values
    missing = df_sales.isnull().sum().sum()
    df_sales = df_sales.fillna(0)
    
    report_content += "## 1. 추정매출 분석\n"
    report_content += f"- **전체 데이터 수**: {len(df_sales):,} 행\n"
    report_content += f"- **결측치 처리**: {missing}개 발견 -> 0으로 대체 완료\n"
    
    # Yearly Trend
    if '당월_매출_금액' in df_sales.columns:
        yearly_sales = df_sales.groupby('기준_년_코드')['당월_매출_금액'].sum()
        report_content += "\n### 📈 연도별 매출 추이\n"
        for year, val in yearly_sales.items():
            report_content += f"- {year}년: {val/1e8:,.1f} 억원\n"

    # Save Filtered
    df_sales.to_csv(os.path.join(directory, 'sales_filtered_2020_2025.csv'), index=False, encoding='utf-8-sig')
    report_content += "\n---\n"

# 2. Store Data Analysis
print("Analyzing Store Data...")
df_store = load_data(files['store'])
if df_store is not None:
    # Handle year filtering
    if '기준_년분기_코드' in df_store.columns:
        df_store['기준_년_코드'] = df_store['기준_년분기_코드'] // 10
    
    if '기준_년_코드' in df_store.columns:
        df_store = df_store[(df_store['기준_년_코드'] >= 2020) & (df_store['기준_년_코드'] <= 2025)]
    
    # Missing Values
    missing = df_store.isnull().sum().sum()
    df_store = df_store.fillna(0)
    
    report_content += "## 2. 점포 현황 분석\n"
    report_content += f"- **전체 데이터 수**: {len(df_store):,} 행\n"
    report_content += f"- **결측치 처리**: {missing}개 발견 -> 0으로 대체 완료\n"
    
    if '점포_수' in df_store.columns:
        top_stores = df_store.groupby('서비스_업종_코드_명')['점포_수'].sum().sort_values(ascending=False).head(5)
        report_content += "\n### 🏪 상위 5개 점포 수 업종\n"
        for sector, val in top_stores.items():
            report_content += f"- {sector}: {val:,.0f} 개 (누적)\n"

    # Save Filtered
    df_store.to_csv(os.path.join(directory, 'store_filtered_2020_2025.csv'), index=False, encoding='utf-8-sig')
    report_content += "\n---\n"

# 3. Rent Analysis
print("Analyzing Rent Data...")
for key in ['rent_small', 'rent_medium']:
    df_rent = load_data(files[key])
    if df_rent is not None:
        title = "소규모 상가" if "소규모" in files[key] else "중대형 상가"
        report_content += f"## 3. {title} 임대가격지수 분석\n"
        rent_cols = [c for c in df_rent.columns if any(y in c for y in ['2020', '2021', '2022', '2023', '2024', '2025'])]
        if rent_cols:
            avg_rent = df_rent[rent_cols].mean()
            report_content += f"- **2020 1Q 지수 평균**: {avg_rent.iloc[0]:.2f}\n"
            report_content += f"- **2025 최신 지수 평균**: {avg_rent.iloc[-1]:.2f}\n"
        report_content += "\n"

# Final Report Save
with open(output_report, 'w', encoding='utf-8-sig') as f:
    f.write(report_content)

print(f"EDA 완료! 리포트 저장됨: {output_report}")
