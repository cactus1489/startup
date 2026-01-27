import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 데이터 경로 설정
data_path = r'c:\Users\dlstj\OneDrive\Desktop\ICB6\daa\seoul_living_population_cleaned.parquet'

# 폰트 및 스타일 설정
import matplotlib.font_manager as fm

# Seaborn 테마를 먼저 설정 (폰트 설정을 초기화할 수 있음)
sns.set_theme(style="whitegrid", palette="muted")

# 한글 폰트 설정 (Windows의 경우 'Malgun Gothic' 사용)
# 만약 맑은 고딕이 없다면 설치된 폰트 중 한글 지원 폰트를 자동으로 찾도록 설정할 수 있습니다.
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def run_visualization():
    # 데이터 파일 존재 여부 확인
    if not os.path.exists(data_path):
        print(f"오류: 파일을 찾을 수 없습니다: {data_path}")
        return

    # 데이터 로드
    df = pd.read_parquet(data_path)
    
    # 컬럼명을 분석하기 쉬운 영문으로 변경
    new_columns = ['hour', 'code', 'gender', 'age_group', 'area', 'population']
    df.columns = new_columns

    # 기본 그래프 크기 설정
    plt.rcParams['figure.figsize'] = (12, 6)
    
    # 1. 시간대별 평균 생활인구 추이 (선 그래프)
    plt.figure()
    hourly_pop = df.groupby('hour')['population'].mean().reset_index()
    sns.lineplot(data=hourly_pop, x='hour', y='population', marker='o', color='#4C72B0', linewidth=2.5)
    plt.title('서울시 시간대별 평균 생활인구 추이', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('시간대 (시)', fontsize=12)
    plt.ylabel('평균 생활인구수 (명)', fontsize=12)
    plt.xticks(range(0, 24))
    plt.tight_layout()
    plt.savefig('hourly_trend.png', dpi=300)
    print("저장됨: hourly_trend.png")

    # 2. 연령대별 총 생활인구 분포 (막대 그래프)
    plt.figure()
    age_pop = df.groupby('age_group')['population'].sum().reset_index().sort_values(by='population', ascending=False)
    sns.barplot(data=age_pop, x='population', y='age_group', palette='viridis')
    plt.title('서울시 연령대별 총 생활인구 분포', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('총 생활인구수 (명)', fontsize=12)
    plt.ylabel('연령대', fontsize=12)
    plt.tight_layout()
    plt.savefig('age_distribution.png', dpi=300)
    print("저장됨: age_distribution.png")

    # 3. 성별 생활인구 비율 (파이 차트)
    plt.figure(figsize=(8, 8))
    gender_pop = df.groupby('gender')['population'].sum()
    
    # 성별 코드 매핑 (0/1을 남성/여성으로 가독성 있게 변경)
    # 데이터 명세에 따라 확인이 필요하지만, 일반적인 구분을 적용합니다.
    labels = ['남성', '여성'] if len(gender_pop) == 2 else [f'성별 {i}' for i in gender_pop.index]
    colors = ['#FF9999', '#66B3FF']
    
    plt.pie(gender_pop, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors, 
            textprops={'fontsize': 14}, explode=(0.05, 0))
    plt.title('서울시 성별 생활인구 비율', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('gender_ratio.png', dpi=300)
    print("저장됨: gender_ratio.png")

if __name__ == "__main__":
    run_visualization()
