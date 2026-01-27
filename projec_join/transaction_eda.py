import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 데이터 로드 경로 설정
base_path = r'C:\Users\dlstj\OneDrive\Desktop\ICB6\projec_join'
data_path = os.path.join(base_path, 'data')
output_data_path = os.path.join(base_path, 'output', 'data')
output_img_path = os.path.join(base_path, 'output', 'images', 'product')

# 1. 데이터 로드
transaction = pd.read_csv(os.path.join(data_path, 'transaction_data.csv'))
product = pd.read_csv(os.path.join(data_path, 'product.csv'))

# 2. Join 수행 (transaction_data <- product)
df_joined = pd.merge(transaction, product, on='PRODUCT_ID', how='left')

# 3. 필요한 컬럼 필터링
columns_to_keep = [
    'household_key', 'BASKET_ID', 'DAY', 'PRODUCT_ID', 
    'DEPARTMENT', 'COMMODITY_DESC', 'QUANTITY', 'SALES_VALUE'
]
df_final = df_joined[columns_to_keep].copy()

# 4. 날짜 파생변수 생성
# week: 1주일 단위 (1~53주)
df_final['week'] = (df_final['DAY'] - 1) // 7 + 1
# month: 30일 단위로 가정 (1~24개월 수준)
df_final['month'] = (df_final['DAY'] - 1) // 30 + 1
# is_weekend: DAY 1이 월요일이라고 가정 (DAY % 7 이 6, 0 이면 주말)
df_final['is_weekend'] = df_final['DAY'].apply(lambda x: 1 if x % 7 in [6, 0] else 0)

# 5. 결과 저장
df_final.to_csv(os.path.join(output_data_path, 'transaction_level_table.csv'), index=False)
print("CSV 파일 저장 완료: transaction_level_table.csv")

# 6. EDA 및 시각화
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# (1) 일자별 거래 건수
plt.figure(figsize=(15, 6))
daily_trans = df_final.groupby('DAY')['BASKET_ID'].nunique()
daily_trans.plot(kind='line', color='skyblue')
plt.title('일자별 거래 건수(Basket Count) 추이')
plt.xlabel('Day')
plt.ylabel('거래 건수')
plt.grid(True)
plt.savefig(os.path.join(output_img_path, 'daily_transaction_count.png'))
plt.close()

# (2) 월별 매출 추이
plt.figure(figsize=(12, 6))
monthly_sales = df_final.groupby('month')['SALES_VALUE'].sum()
sns.barplot(x=monthly_sales.index, y=monthly_sales.values, palette='viridis')
plt.title('월별 총 매출액 추이')
plt.xlabel('Month (30일 단위)')
plt.ylabel('총 매출액 ($)')
plt.savefig(os.path.join(output_img_path, 'monthly_sales_trend.png'))
plt.close()

# (3) 주중/주말 매출 비중
plt.figure(figsize=(8, 6))
weekend_sales = df_final.groupby('is_weekend')['SALES_VALUE'].sum()
plt.pie(weekend_sales, labels=['평일', '주말'], autopct='%1.1f%%', startangle=140, colors=['lightcoral', 'lightgreen'])
plt.title('평일 vs 주말 매출 비중')
plt.savefig(os.path.join(output_img_path, 'weekend_sales_ratio.png'))
plt.close()

# (4) 상위 상품군(Department)별 매출
plt.figure(figsize=(12, 8))
dept_sales = df_final.groupby('DEPARTMENT')['SALES_VALUE'].sum().sort_values(ascending=False).head(10)
sns.barplot(x=dept_sales.values, y=dept_sales.index, palette='magma')
plt.title('매출 상위 10개 부서(Department)')
plt.xlabel('총 매출액 ($)')
plt.ylabel('Department')
plt.savefig(os.path.join(output_img_path, 'top_dept_sales.png'))
plt.close()

print("시각화 이미지 저장 완료.")
