import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
import requests

# 페이지 설정
st.set_page_config(page_title="2030 예비 창업자 상권 분석 대시보드 v2.6", layout="wide")

# 데이터 경로
CSV_PATH = os.path.join(os.path.dirname(__file__), '서울시_상권분석서비스(추정매출-상권)_2020-2025.csv')
SEOUL_GEOJSON_URL = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/kostat/2013/json/seoul_municipalities_geo_simple.json"

@st.cache_data
def load_and_process_data():
    """대용량 CSV 데이터를 로드하고 2020년 이후 모든 데이터를 집계합니다."""
    use_cols = [
        '기준_년분기_코드', '상권_코드_명', '서비스_업종_코드_명', 
        '당월_매출_금액', '연령대_20_매출_금액', '연령대_30_매출_금액'
    ]
    
    df_list = []
    try:
        df_iter = pd.read_csv(CSV_PATH, encoding='utf-8', usecols=use_cols, chunksize=200000)
        for chunk in df_iter:
            df_list.append(chunk)
        df = pd.concat(df_list)
        
        # 연도 컬럼 추출
        df['year'] = (df['기준_년분기_코드'] // 10).astype(int)
        
        # 2030 합산 매출 미리 계산
        df['sales_2030'] = df['연령대_20_매출_금액'] + df['연령대_30_매출_금액']
        
        grouped = df.groupby(['상권_코드_명', '서비스_업종_코드_명', 'year', '기준_년분기_코드']).agg({
            '당월_매출_금액': 'sum',
            '연령대_20_매출_금액': 'sum',
            '연령대_30_매출_금액': 'sum',
            'sales_2030': 'sum'
        }).reset_index()
        
        return grouped
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return None

@st.cache_data
def get_seoul_geojson():
    """서울시 자치구 GeoJSON 데이터를 가져옵니다."""
    try:
        response = requests.get(SEOUL_GEOJSON_URL)
        return response.json()
    except:
        return None

# 자치구 매핑 데이터
GU_MAPPING = {
    '강남역': '강남구', '역삼역': '강남구', '압구정': '강남구', '가로수길': '강남구',
    '홍대입구역': '마포구', '망원역': '마포구', '연남동': '마포구',
    '명동': '중구', '을지로': '중구', '북창동': '중구', '종로3가': '종로구', '인사동': '종로구',
    '성수동': '성동구', '건대입구역': '광진구', '이태원': '용산구', '한남동': '용산구',
    '잠실역': '송파구', '천호역': '강동구', '노원역': '노원구', '대학로': '종로구',
    '가산디지털단지': '금천구', '구로디지털단지': '구로구', '여의도': '영등포구'
}

GU_RENT_DATA = {
    '중구': 16.5, '강남구': 14.8, '서초구': 12.5, '마포구': 10.2, '성동구': 9.5,
    '용산구': 9.0, '종로구': 8.8, '송파구': 8.5, '영등포구': 8.0, '광진구': 7.5,
    '서대문구': 7.2, '동작구': 7.0, '강동구': 6.8, '양천구': 6.5, '성북구': 6.2,
    '관악구': 6.0, '동대문구': 5.8, '구로구': 5.5, '금천구': 5.2, '강서구': 5.0,
    '노원구': 4.8, '중랑구': 4.5, '은평구': 4.2, '강북구': 4.0, '도봉구': 3.8, '기타': 5.0
}

YOUTH_ASSET_STATS = {
    '평균 자산': '3억 1,583만원',
    '평균 순자산': '2억 2,158만원',
    '평균 부채': '9,425만원'
}

def main():
    st.title("🚀 2030 예비 창업자 '안전 창업 지대' 분석 v2.6")
    st.markdown("전체 상권 데이터 뿐만 아니라 **인기 아이템인 '한식음식점'의 성공 가설**을 별도로 집중 분석합니다.")

    # --- 2030 자산 현황 KPI ---
    with st.expander("💳 2024년 2030세대 자산 실태 (창업 자금 참고)", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.metric("🏘️ 평균 자산", YOUTH_ASSET_STATS['평균 자산'], "-6.0%")
        c2.metric("💰 평균 순자산", YOUTH_ASSET_STATS['평균 순자산'], "-6.4%")
        c3.metric("💳 평균 부채", YOUTH_ASSET_STATS['평균 부채'], "-5.2%")
        st.caption("출처: 2024년 가계금융복지조사 요약")

    with st.spinner("데이터 분석 중..."):
        data = load_and_process_data()
        geojson = get_seoul_geojson()

    if data is None: return

    # --- 사이드바 필터 ---
    st.sidebar.header("📊 데이터 탐색 설정")
    available_years = sorted(data['year'].unique(), reverse=True)
    selected_year = st.sidebar.selectbox("분석 대상 연도", available_years, index=0)
    selected_age = st.sidebar.radio("집중 분석 연령대", ["전체(2030)", "20대", "30대"], key="age_selector")
    
    all_categories = sorted(data['서비스_업종_코드_명'].unique())
    selected_categories = st.sidebar.multiselect("관심 업종 선택 (필터링)", options=all_categories)

    # --- 공통 데이터 가공 ---
    current_df = data[data['year'] == selected_year].copy()
    if selected_categories:
        current_df = current_df[current_df['서비스_업종_코드_명'].isin(selected_categories)]

    # 비중 컬럼 생성
    for col in [('ratio_20', '연령대_20_매출_금액'), ('ratio_30', '연령대_30_매출_금액'), ('ratio_2030', 'sales_2030')]:
        current_df[col[0]] = (current_df[col[1]] / current_df['당월_매출_금액'] * 100).round(1).fillna(0)

    # 전년 대비 성장률 계산
    prior_year = selected_year - 1
    past_year_df = data[data['year'] == prior_year]
    
    def get_analysis_table(df_curr, df_prev):
        curr_stats = df_curr.groupby(['상권_코드_명', '서비스_업종_코드_명']).agg({
            '당월_매출_금액': 'mean', 'ratio_20': 'mean', 'ratio_30': 'mean', 'ratio_2030': 'mean'
        }).reset_index()
        prev_stats = df_prev.groupby(['상권_코드_명', '서비스_업종_코드_명'])['당월_매출_금액'].mean().reset_index()
        merged = pd.merge(curr_stats, prev_stats, on=['상권_코드_명', '서비스_업종_코드_명'], how='left', suffixes=('_curr', '_prev'))
        merged['growth'] = ((merged['당월_매출_금액_curr'] - merged['당월_매출_금액_prev']) / merged['당월_매출_금액_prev'] * 100).round(2).fillna(0)
        return merged

    final_analysis = get_analysis_table(current_df, past_year_df)
    target_ratio_col = 'ratio_2030' if selected_age == "전체(2030)" else ("ratio_20" if selected_age == "20대" else "ratio_30")

    # --- 탭 구성 ---
    tab_korean, tab_summary, tab_map, tab_keywords, tab_trend = st.tabs([
        "🍲 한식음식점 집중 분석", "🚀 가설 검증: 통합 안전지", "🗺️ 서울 지도 & 지가", "🔑 연령별 인기 키워드", "📈 연도별 매출 추이"
    ])

    with tab_korean:
        st.subheader(f"🍲 2030 한식음식점 창업 성공 가설 검증 ({selected_year}년)")
        st.markdown(f"**가설**: \"한식 업종 역시 {selected_age} 매출 비중이 50%가 넘고 매출이 성장하는 곳이 안전하다.\"")
        
        # 한식 전용 필터링
        korean_df_curr = current_df[current_df['서비스_업종_코드_명'] == '한식음식점']
        korean_df_prev = past_year_df[past_year_df['서비스_업종_코드_명'] == '한식음식점']
        
        if not korean_df_curr.empty:
            korean_analysis = get_analysis_table(korean_df_curr, korean_df_prev)
            
            # 가설 적용 (비중 50%↑ + 성장률 > 0)
            k_safe_mask = (korean_analysis[target_ratio_col] >= 50) & (korean_analysis['growth'] > 0)
            korean_analysis['Safe'] = k_safe_mask.map({True: '✅ 한식 안전지', False: '일반 지역'})
            
            c_k1, c_k2 = st.columns(2)
            with c_k1:
                # 한식 성장률 비교
                fig_k_growth = px.box(korean_analysis, x='Safe', y='growth', color='Safe', 
                                    title="한식 업종 내 안전지 vs 일반 지역 성장률 분포")
                st.plotly_chart(fig_k_growth, use_container_width=True)
            with c_k2:
                # 안전지 리스트
                k_top = korean_analysis[k_safe_mask].sort_values(by=target_ratio_col, ascending=False).head(10)
                st.write("**💎 한식 창업 추천 '안전지' TOP 10**")
                if not k_top.empty:
                    st.dataframe(k_top[['상권_코드_명', target_ratio_col, 'growth']].rename(columns={
                        '상권_코드_명': '추천 상권명', target_ratio_col: f'{selected_age} 비중(%)', 'growth': '성장률(%)'
                    }), use_container_width=True, hide_index=True)
                else:
                    st.warning("한식 업종 중 가설에 부합하는 상권이 현재 연도에는 보이지 않습니다.")
            
            st.divider()
            st.markdown(f"💡 **인사이트**: {selected_year}년 한식 업종 내에서 2030 소비 비중이 50%를 넘는 상권은 전체 한식 상권 중 **{(len(korean_analysis[korean_analysis[target_ratio_col]>=50])/len(korean_analysis)*100):.1f}%**입니다.")
        else:
            st.warning("한식음식점 데이터를 찾을 수 없습니다.")

    with tab_summary:
        st.subheader(f"✅ {selected_year}년 전체 업종 가설 입증 (통합)")
        final_analysis['Zone'] = '기타 지역'
        safe_mask = (final_analysis[target_ratio_col] >= 50) & (final_analysis['growth'] > 0)
        final_analysis.loc[safe_mask, 'Zone'] = '✅ 통합 안전지'
        
        sc1, sc2 = st.columns(2)
        with sc1:
            avg_g = final_analysis.groupby('Zone')['growth'].mean().reset_index()
            st.plotly_chart(px.bar(avg_g, x='Zone', y='growth', color='Zone', title="그룹별 평균 성장률 대조"), use_container_width=True)
        with sc2:
            st.write(f"**💎 {selected_age} 추천 '통합 안전지' TOP 10**")
            st.dataframe(final_analysis[safe_mask].sort_values(by=target_ratio_col, ascending=False).head(10)[['상권_코드_명', '서비스_업종_코드_명', target_ratio_col, 'growth']].rename(columns={
                '상권_코드_명': '상권', '서비스_업종_코드_명': '업종', target_ratio_col: '비중(%)', 'growth': '성장(%)'
            }), use_container_width=True, hide_index=True)

    with tab_map:
        st.subheader(f"📍 {selected_year}년 서울 상권 매출 & 임대료")
        map_data = current_df.copy()
        seoul_gus = list(GU_RENT_DATA.keys())
        map_data['GU'] = map_data['상권_코드_명'].apply(lambda x: next((gu for gu in seoul_gus if gu in x), 
                                                           next((gu for key, gu in GU_MAPPING.items() if key in x), "기타")))
        
        map_col = '연령대_20_매출_금액' if selected_age == "20대" else ('연령대_30_매출_금액' if selected_age == "30대" else 'sales_2030')
        gu_sales = map_data.groupby('GU')[map_col].sum().reset_index()
        
        if geojson:
            fig_map = px.choropleth_mapbox(
                gu_sales, geojson=geojson, locations="GU", featureidkey="properties.name",
                color=map_col, mapbox_style="carto-positron", zoom=10, center={"lat": 37.5665, "lon": 126.9780},
                opacity=0.7, color_continuous_scale="Viridis",
                title=f"서울 자치구별 {selected_year}년 {selected_age} 매출 분포"
            )
            fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
            st.plotly_chart(fig_map, use_container_width=True)
            
            st.divider()
            # 지역별 전략 테이블
            gu_category_sales = map_data.groupby(['GU', '서비스_업종_코드_명'])[map_col].sum().reset_index()
            top_idx = gu_category_sales.groupby('GU')[map_col].idxmax()
            gu_best = gu_category_sales.loc[top_idx].rename(columns={'서비스_업종_코드_명': '1위 업종'})
            
            summary = pd.merge(gu_sales.rename(columns={map_col: '매출'}), gu_best[['GU', '1위 업종']], on='GU')
            summary['임대료'] = summary['GU'].map(GU_RENT_DATA)
            summary['효율성'] = (summary['매출'] / (summary['임대료'] * 1000000)).round(2) # 백만원 → 원 단위로 변환
            summary['매출(억)'] = (summary['매출'] / 100000000).round(1)
            
            st.dataframe(summary[['GU', '매출(억)', '임대료', '1위 업종', '효율성']].rename(columns={'GU': '지역', '임대료': '지가(만원)'}), use_container_width=True, hide_index=True)
        else:
            st.error("지도 데이터를 불러올 수 없습니다.")

    with tab_keywords:
        st.subheader("🔑 연령별 인기 업종 랭킹")
        c2, c3 = st.columns(2)
        with c2:
            st.success(f"🏢 **20대 매출 TOP 5 ({selected_year})**")
            st.write(current_df.groupby('서비스_업종_코드_명')['연령대_20_매출_금액'].sum().sort_values(ascending=False).head(5))
        with c3:
            st.info(f"🏠 **30대 매출 TOP 5 ({selected_year})**")
            st.write(current_df.groupby('서비스_업종_코드_명')['연령대_30_매출_금액'].sum().sort_values(ascending=False).head(5))

    with tab_trend:
        st.subheader("📈 서울 시계열 매출 추이 (2020-2024)")
        y_group = data.groupby('year').agg({'당월_매출_금액': 'sum', 'sales_2030': 'sum'}).reset_index()
        fig_trend = px.line(y_group, x='year', y=['당월_매출_금액', 'sales_2030'], markers=True, title="연도별 매출 규모 변화")
        st.plotly_chart(fig_trend, use_container_width=True)

    st.sidebar.markdown("---")
    st.sidebar.caption("Data Source: 서울시 상권분석 / 2024 자산통계")
    st.sidebar.info("v2.6 한식 집중 분석 모드")

if __name__ == "__main__":
    main()
