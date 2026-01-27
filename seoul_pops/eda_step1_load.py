import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

# 데이터 경로 설정
data_path = r'c:\Users\dlstj\OneDrive\Desktop\ICB6\daa\seoul_living_population_cleaned.parquet'

# 시각화 설정 (한글 폰트)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.family'] = 'Malgun Gothic' # Seaborn 테마 설정 후 다시 설정

def run_comprehensive_eda():
    print(f"--- 데이터 로딩 시작: {data_path} ---")
    if not os.path.exists(data_path):
        print(f"Error: 파일을 찾을 수 없습니다: {data_path}")
        return

    # 1. 데이터 로드 및 전처리
    df = pd.read_parquet(data_path)
    new_columns = ['hour', 'code', 'gender', 'age_group', 'area', 'population']
    df.columns = new_columns
    
    # 보고서용 텍스트 리스트
    report_lines = ["# 서울시 생활인구 분석 보고서\n"]
    report_lines.append("## 1. 데이터 기본 정보\n")
    report_lines.append(f"- 데이터 경로: {data_path}\n")
    report_lines.append(f"- 전체 데이터 수: {len(df):,}\n")
    
    # 2. 시각화 5개 이상 추가
    print("\n--- 시각화 생성 중 ---")
    
    # (1) 시간대별 평균 생활인구 추이
    plt.figure(figsize=(10, 5))
    hourly_pop = df.groupby('hour')['population'].mean().reset_index()
    sns.lineplot(data=hourly_pop, x='hour', y='population', marker='o')
    plt.title('시간대별 평균 생활인구 추이')
    img1 = 'viz_1_hourly_trend.png'
    plt.savefig(img1, dpi=300)
    report_lines.append(f"\n### 1.1 시간대별 평균 생활인구 추이\n![Hourly Trend]({os.path.abspath(img1)})\n")

    # (2) 연령대별 총 생활인구 분포
    plt.figure(figsize=(10, 5))
    age_pop = df.groupby('age_group')['population'].sum().reset_index().sort_values(by='population', ascending=False)
    sns.barplot(data=age_pop, x='population', y='age_group', palette='viridis')
    plt.title('연령대별 총 생활인구 분포')
    img2 = 'viz_2_age_distribution.png'
    plt.savefig(img2, dpi=300)
    report_lines.append(f"\n### 1.2 연령대별 총 생활인구 분포\n![Age Distribution]({os.path.abspath(img2)})\n")

    # (3) 성별 생활인구 비율
    plt.figure(figsize=(7, 7))
    gender_pop = df.groupby('gender')['population'].sum()
    labels = ['남성', '여성'] if len(gender_pop) == 2 else gender_pop.index
    plt.pie(gender_pop, labels=labels, autopct='%1.1f%%', startangle=140, colors=['#66B3FF', '#FF9999'])
    plt.title('성별 생활인구 비율')
    img3 = 'viz_3_gender_ratio.png'
    plt.savefig(img3, dpi=300)
    report_lines.append(f"\n### 1.3 성별 생활인구 비율\n![Gender Ratio]({os.path.abspath(img3)})\n")

    # (4) 성별/연령대별 생활인구 패턴 (Heatmap)
    plt.figure(figsize=(12, 6))
    pivot_table = df.pivot_table(index='age_group', columns='gender', values='population', aggfunc='mean')
    pivot_table.columns = ['남성', '여성'] if len(pivot_table.columns) == 2 else pivot_table.columns
    sns.heatmap(pivot_table, annot=True, fmt=".0f", cmap='YlGnBu')
    plt.title('성별 및 연령대별 평균 생활인구 히트맵')
    img4 = 'viz_4_gender_age_heatmap.png'
    plt.savefig(img4, dpi=300)
    report_lines.append(f"\n### 1.4 성별 및 연령대별 평균 생활인구 히트맵\n![Gender Age Heatmap]({os.path.abspath(img4)})\n")

    # (5) 성별에 따른 생활인구 분포 (Box Plot)
    plt.figure(figsize=(8, 6))
    sns.boxplot(data=df, x='gender', y='population', palette='Set2')
    plt.title('성별 생활인구분포 (Box Plot)')
    img5 = 'viz_5_gender_boxplot.png'
    plt.savefig(img5, dpi=300)
    report_lines.append(f"\n### 1.5 성별 생활인구분포\n![Gender Boxplot]({os.path.abspath(img5)})\n")

    # (6) 상위 10개 지역(Area) 생활인구
    plt.figure(figsize=(10, 6))
    top_areas = df.groupby('area')['population'].sum().nlargest(10).reset_index()
    sns.barplot(data=top_areas, x='population', y='area', palette='magma')
    plt.title('생활인구 상위 10개 지역')
    img6 = 'viz_6_top_areas.png'
    plt.savefig(img6, dpi=300)
    report_lines.append(f"\n### 1.6 생활인구 상위 10개 지역\n![Top Areas]({os.path.abspath(img6)})\n")

    # 3. 교차표 (Cross-tabulation)
    print("\n--- 교차표 생성 중 ---")
    report_lines.append("\n## 2. 데이터 교차표 분석\n")
    
    # (1) 성별 x 연령대 교차표
    ct_gender_age = pd.crosstab(df['gender'], df['age_group'], values=df['population'], aggfunc='sum').fillna(0)
    ct_gender_age.index = ['남성', '여성'] if len(ct_gender_age.index) == 2 else ct_gender_age.index
    print("\n[성별 x 연령대 총 생활인구 교차표]")
    print(ct_gender_age)
    report_lines.append("\n### 2.1 성별 x 연령대 총 생활인구\n")
    report_lines.append(ct_gender_age.to_markdown() + "\n")

    # (2) 시간대(4시간 단위 요약) x 성별 교차표
    df['hour_group'] = (df['hour'] // 4) * 4
    ct_hour_gender = pd.crosstab(df['hour_group'], df['gender'], values=df['population'], aggfunc='mean').fillna(0)
    ct_hour_gender.columns = ['남성', '여성'] if len(ct_hour_gender.columns) == 2 else ct_hour_gender.columns
    print("\n[시간대 요약 x 성별 평균 생활인구 교차표]")
    print(ct_hour_gender)
    report_lines.append("\n### 2.2 시간대 요약(4h) x 성별 평균 생활인구\n")
    report_lines.append(ct_hour_gender.to_markdown() + "\n")

    # 4. 마크다운 파일 저장
    report_path = 'eda_report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.writelines(report_lines)
    print(f"\n--- 분석 결과가 {report_path}에 저장되었습니다. ---")

if __name__ == "__main__":
    run_comprehensive_eda()
