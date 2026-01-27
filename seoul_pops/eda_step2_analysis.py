import pandas as pd
import os

# 데이터 경로 설정
data_path = r'c:\Users\dlstj\OneDrive\Desktop\ICB6\daa\seoul_living_population_cleaned.parquet'

def run_analysis():
    if not os.path.exists(data_path):
        print(f"Error: 파일을 찾을 수 없습니다: {data_path}")
        return

    # 데이터 로드
    df = pd.read_parquet(data_path)
    
    # 컬럼명 확인 및 영어로 변경 (터미널 한글 깨짐 방지 및 분석 편의성)
    print("기존 컬럼명:", df.columns.tolist())
    
    # 컬럼 매핑 (시간대, 자치구코드, 성별, 연령대, 행정동, 총생활인구수 순서)
    new_columns = ['hour', 'code', 'gender', 'age_group', 'area', 'population']
    df.columns = new_columns
    
    print("\n--- 분석 결과 요약 ---")
    
    # 1. 시간대별 평균 생활인구
    hourly_pop = df.groupby('hour')['population'].mean().reset_index()
    print("\n1. 시간대별 평균 인구 (상위 5개):")
    print(hourly_pop.sort_values(by='population', ascending=False).head())
    
    # 2. 성별 생활인구 합계
    gender_pop = df.groupby('gender')['population'].sum().reset_index()
    print("\n2. 성별 총 생활인구 합계:")
    print(gender_pop)
    
    # 3. 연령대별 생활인구 합계
    age_pop = df.groupby('age_group')['population'].sum().reset_index()
    print("\n3. 연령대별 총 생활인구 합계 (상위 5개):")
    print(age_pop.sort_values(by='population', ascending=False).head())
    
    # 결과 저장 (선택 사항)
    hourly_pop.to_csv('hourly_population_summary.csv', index=False)
    print("\n요약 데이터가 'hourly_population_summary.csv'에 저장되었습니다.")

if __name__ == "__main__":
    run_analysis()
