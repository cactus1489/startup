import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# 폰트 설정 (한글 깨짐 방지)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 경로
CSV_PATH = 'youth_startup/서울시_상권분석서비스(추정매출-상권)_2020-2025.csv'

def perform_eda():
    print("--- 2030 예비 창업자 생존 전략 EDA 시작 ---")
    
    # 분석에 필요한 컬럼만 추출 (메모리 효율화)
    use_cols = [
        '기준_년분기_코드', '상권_코드_명', '서비스_업종_코드_명', 
        '당월_매출_금액', '연령대_20_매출_금액', '연령대_30_매출_금액'
    ]
    
    print("1. 데이터 로딩 중 (최신 데이터 위주)...")
    try:
        # 전체를 다 읽기엔 크므로, 일단 읽어와서 상권/업종별로 집계
        # 기준_년분기_코드가 20241, 20242 등 최근 데이터를 필터링하기 위해 반복문 사용 가능
        df_iter = pd.read_csv(CSV_PATH, encoding='utf-8', usecols=use_cols, chunksize=100000)
        df_list = []
        for chunk in df_iter:
            # 2023년 이후 데이터만 수집
            chunk = chunk[chunk['기준_년분기_코드'] >= 20231]
            df_list.append(chunk)
        df = pd.concat(df_list)
        print(f"로딩 완료. (대상 행 수: {len(df):,})")
    except Exception as e:
        print(f"오류 발생: {e}")
        return

    # 2. 2030 매출 비중 계산
    print("2. 2030 매출 비중 산출 중...")
    df['sales_2030'] = df['연령대_20_매출_금액'] + df['연령대_30_매출_금액']
    
    # 상권 및 업종별 집계
    grouped = df.groupby(['상권_코드_명', '서비스_업종_코드_명', '기준_년분기_코드']).agg({
        '당월_매출_금액': 'sum',
        'sales_2030': 'sum'
    }).reset_index()

    # 상권/업종별 평균 2030 비중 계산 (최근 2분기 기준)
    recent_df = grouped[grouped['기준_년분기_코드'] >= 20241].copy()
    recent_df['ratio_2030'] = (recent_df['sales_2030'] / recent_df['당월_매출_금액']) * 100
    
    # 가설: 2030 비중이 50% 이상인 곳
    safe_zones = recent_df[recent_df['ratio_2030'] > 50].copy()
    
    # 3. 성장성 분석 (2023년 평균 대비 2024년 성장률)
    print("3. 가설 검증 (매출 성장성 분석)...")
    avg_2023 = grouped[grouped['기준_년분기_코드'].between(20231, 20234)].groupby(['상권_코드_명', '서비스_업종_코드_명'])['당월_매출_금액'].mean().reset_index()
    avg_2024 = grouped[grouped['기준_년분기_코드'] >= 20241].groupby(['상권_코드_명', '서비스_업종_코드_명'])['당월_매출_금액'].mean().reset_index()
    
    growth = pd.merge(avg_2023, avg_2024, on=['상권_코드_명', '서비스_업종_코드_명'], suffixes=('_2023', '_2024'))
    growth['growth_rate'] = (growth['당월_매출_금액_2024'] - growth['당월_매출_금액_2023']) / growth['당월_매출_금액_2023'] * 100
    
    # 최종 타겟: 2030 비중 > 50% & 성장률 > 0
    final_targets = pd.merge(safe_zones, growth[['상권_코드_명', '서비스_업종_코드_명', 'growth_rate']], on=['상권_코드_명', '서비스_업종_코드_명'])
    final_targets = final_targets[final_targets['growth_rate'] > 0].sort_values(by='ratio_2030', ascending=False)
    
    print("\n--- [결과] 2030 예비 창업자를 위한 추천 창업지 (TOP 5) ---")
    print(final_targets[['상권_코드_명', '서비스_업종_코드_명', 'ratio_2030', 'growth_rate']].head(10))
    
    # 4. 시각화
    print("\n4. 시각화 파일 생성 중...")
    plt.figure(figsize=(12, 6))
    top_10 = final_targets.head(10)
    sns.barplot(data=top_10, x='ratio_2030', y='상권_코드_명', hue='서비스_업종_코드_명')
    plt.title('2030 매출 비중 50% 이상 & 성장 중인 유망 상권/업종')
    plt.xlabel('2030 매출 비중 (%)')
    plt.ylabel('상권명')
    plt.savefig('youth_startup/startup_recommendation.png')
    print("시각화 완료: youth_startup/startup_recommendation.png")

if __name__ == "__main__":
    perform_eda()
