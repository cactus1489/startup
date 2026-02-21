import streamlit as st
import pandas as pd
import numpy as np
import os
import streamlit.components.v1 as components
import plotly.express as px
import altair as alt

# --- Setup & Config ---
st.set_page_config(
    page_title="서울시 카페 창업 적합도 (Coffee Index) 보고서", 
    page_icon="☕", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS (Premium Style) ---
st.markdown("""
<style>
    /* Global Font Settings */
    html, body, [class*="css"] {
        font-family: 'Pretendard', 'Apple SD Gothic Neo', 'Helvetica Neue', sans-serif !important;
        color: #31333E;
    }
    
    /* Overall Text Size Increase */
    .report-text, p, li, span, div.stMarkdown {
        font-size: 20px !important;
        line-height: 1.8 !important;
    }
    
    /* Sidebar Text Size */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        font-size: 18px !important;
    }
    
    /* Radio Button / Navigation Text */
    [data-testid="stSidebar"] .st-emotion-cache-17l69qf {
        font-size: 18px !important;
    }

    /* Tabs Text Size */
    button[data-baseweb="tab"] p {
        font-size: 22px !important;
        font-weight: 600 !important;
    }

    h1 { font-size: 42px !important; margin-bottom: 20px; border-bottom: 3px solid #f1f5f9; padding-bottom: 10px; }
    h2 { font-size: 34px !important; margin-top: 30px; }
    h3 { font-size: 28px !important; }
    h4 { font-size: 24px !important; }

    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
        width: 350px !important;
    }
    
    .stTable {
        font-size: 18px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Data Loading (Using Relative Paths for Deployment) ---
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    results_path = os.path.join(current_dir, 'coffee_index_results.csv')
    
    # Robust path finding for coordinate data
    confirmed_dir = os.path.join(current_dir, '../a_confirmed')
    density_path = ""
    
    if os.path.exists(confirmed_dir):
        # Look for the file regardless of NFC/NFD normalization
        files = os.listdir(confirmed_dir)
        for f in files:
            if "서울시_상권_좌표_밀집도_데이터" in f and f.endswith(".csv"):
                density_path = os.path.join(confirmed_dir, f)
                break
    
    if os.path.exists(results_path):
        df_results = pd.read_csv(results_path)
        if density_path and os.path.exists(density_path):
            try:
                df_geo = pd.read_csv(density_path, encoding='utf-8')
            except:
                try:
                    df_geo = pd.read_csv(density_path, encoding='cp949')
                except:
                    return df_results, pd.DataFrame()
            
            df_merged = pd.merge(df_results, df_geo[['상권명', '위도', '경도', '총_점포수']], 
                                 left_on='상권_코드_명', right_on='상권명', how='left')
            df_geo['Is_Target'] = df_geo['상권명'].isin(df_results['상권_코드_명'])
            return df_merged, df_geo
        return df_results, pd.DataFrame()
    return pd.DataFrame(), pd.DataFrame()

df, df_full_geo = load_data()

# --- Sidebar Navigation ---
st.sidebar.title("☕ Coffee Index")
st.sidebar.markdown("서울시 카페 창업 적합도 분석")
st.sidebar.markdown("---")

page = st.sidebar.radio("보고서 목차", [
    "0. 대시보드 개요",
    "1. 문제 정의 (Problem)",
    "2. 데이터 및 산출 로직",
    "3. 지표 분석 및 시각화",
    "4. 공간 분석 (GIS Map)",
    "5. 인사이트 및 전략",
    "6. 검증 가설 및 결론"
])

# --- Content ---
if page == "0. 대시보드 개요":
    st.title("🏆 서울시 카페 창업 적합도 지수 (Coffee Index) 최종 보고서 (v1.1)")
    
    st.markdown('<p class="report-text">본 보고서는 오프라인 실물 지표(매출, 유동, 임대 등)에 온라인 관심도 지표를 새롭게 융합한 <strong>"Coffee Index"</strong> 산출 결과를 제공합니다.</p>', unsafe_allow_html=True)
    
    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        top_region = df.sort_values('Coffee_Index', ascending=False).iloc[0]
        col1.metric("최적 상권", top_region['상권_코드_명'])
        col2.metric("최고 Index", f"{top_region['Coffee_Index']:.1f}")
        col3.metric("대상 상권 수", len(df))
        col4.metric("분석 기간", "2020Q1-2024Q4")
        
        st.markdown("---")
        st.subheader("📍 Target Regions (Hidden Gems)")
        fig_rank = px.bar(df.sort_values('Coffee_Index', ascending=True), 
                          y='상권_코드_명', x='Coffee_Index', 
                          orientation='h', color='Coffee_Index',
                          color_continuous_scale='Reds',
                          title="상권별 Coffee Index 랭킹")
        st.plotly_chart(fig_rank, use_container_width=True)

elif page == "1. 문제 정의 (Problem)":
    st.header("1. 문제 정의 (Problem Definition)")
    st.markdown("""
    <div class="report-text">
    <strong>"단순히 매출이 높은 곳이 창업하기 가장 좋은 곳인가?"</strong><br><br>
    <ul>
        <li><strong>한계점</strong>: 기존 분석은 매출 규모가 크거나 유동인구가 많은 대형 상권(예: 강남, 중구)을 1순위로 추천하는 경향이 있었음. 그러나 이곳은 고정비(임대료)와 경쟁 과열(점포수)로 인해 실제 수익성은 낮을 수 있음.</li>
        <li><strong>분석 목표</strong>: 수요와 온라인 관심도는 높게 유지되면서, 임대료 폭등이 적고 공실 및 점포 쏠림이 덜한 <strong>'숨겨진 꿀상권(Hidden Gem)'</strong>을 도출함.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("💡 분석 프레임워크: Coffee Index")
    c1, c2 = st.columns(2)
    with c1:
        st.info("➕ **가점 요소 (수요/성장)**\n- 당월 추정매출액 (25%)\n- 총 유동인구수 (20%)\n- 네이버 검색 트렌드 (15%)")
    with c2:
        st.warning("➖ **감점 요소 (비용/리스크)**\n- 상가 임대가격지수 (15%)\n- 커피 점포수/경쟁도 (15%)\n- 소규모 상가 공실률 (10%)")

elif page == "2. 데이터 및 산출 로직":
    st.header("2. 데이터 구조 및 전처리")
    
    st.markdown("""
    <div class="report-text">
    <strong>2.1 데이터 소스</strong>
    <ul>
        <li>서울시 상권분석서비스 (추정매출, 점포, 유동인구)</li>
        <li>한국부동산원 (임대가격지수, 공실률)</li>
        <li>네이버 데이터랩 (지역별 검색 트렌드)</li>
    </ul>
    
    <strong>2.2 지수 산출 로직 (Methodology)</strong>
    <br><code>Coffee Index = (Positive Factors - Negative Factors)</code>를 0~100으로 정규화
    <br><code>Trend Index = Momentum(60%) + Concentration(25%) + Sustainability(15%)</code>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("🛠️ 전처리 & 정합성 이슈 해결 내용"):
        st.markdown("""
        - **공간 정합성**: 서울시 상권코드와 부동산/공실률 데이터의 '상권명' 매핑 (`regional_trend_index_mapped.csv`)
        - **시계열 정렬**: 분기(Quarter) 단위 통합 및 결측치 보정 (ffill/bfill)
        - **스케일 정규화**: 단위가 다른 6개 지표를 `Min-Max Scaling` 적용
        """)

elif page == "3. 지표 분석 및 시각화":
    st.header("3. 지표별 상세 분석")
    
    if df.empty:
        st.error("데이터를 불러올 수 없습니다.")
    else:
        # Comparison with Average Section
        st.subheader("🎯 핵심 상권 상세 분석 (Detailed Comparison)")
        st.markdown("최상위 랭킹 상권들과 14개 상권 평균 지표를 정밀 비교합니다.")
        
        # Display the comparison image
        current_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(current_dir, 'score_comparison_v2.png')
        if os.path.exists(img_path):
            st.image(img_path, caption="Coffee Index Detail Comparison: Market Leaders vs Average", use_container_width=True)
        
        st.markdown("---")
        
        # Leader Analysis Tables
        c1, c2 = st.columns(2)
        avg_scores = df.mean(numeric_only=True)
        
        with c1:
            st.markdown("#### 🥇 양재역 (저위험 안정형)")
            y = df[df['상권_코드_명']=='양재역'].iloc[0]
            st.table(pd.DataFrame({
                "지표": ["매출 점수", "유동인구 점수", "트렌드 점수", "임대료 리스크", "점포수 리스크", "공실률 리스크"],
                "양재역": [f"{y['Sales_Score']:.1f}", f"{y['Pop_Score']:.1f}", f"{y['Trend_Score']:.1f}", f"{y['Rent_Score']:.1f}", f"{y['Store_Score']:.1f}", f"{y['Vacancy_Score']:.1f}"],
                "평균 대비": [f"{y['Sales_Score']-avg_scores['Sales_Score']:+.1f}", f"{y['Pop_Score']-avg_scores['Pop_Score']:+.1f}", f"{y['Trend_Score']-avg_scores['Trend_Score']:+.1f}", 
                           f"{y['Rent_Score']-avg_scores['Rent_Score']:+.1f}", f"{y['Store_Score']-avg_scores['Store_Score']:+.1f}", f"{y['Vacancy_Score']-avg_scores['Vacancy_Score']:+.1f}"]
            }))

        with c2:
            st.markdown("#### 🥈 성신여대 (고수익 트렌드형)")
            s = df[df['상권_코드_명']=='성신여대'].iloc[0]
            st.table(pd.DataFrame({
                "지표": ["매출 점수", "유동인구 점수", "트렌드 점수", "임대료 리스크", "점포수 리스크", "공실률 리스크"],
                "성신여대": [f"{s['Sales_Score']:.1f}", f"{s['Pop_Score']:.1f}", f"{s['Trend_Score']:.1f}", f"{s['Rent_Score']:.1f}", f"{s['Store_Score']:.1f}", f"{s['Vacancy_Score']:.1f}"],
                "평균 대비": [f"{s['Sales_Score']-avg_scores['Sales_Score']:+.1f}", f"{s['Pop_Score']-avg_scores['Pop_Score']:+.1f}", f"{s['Trend_Score']-avg_scores['Trend_Score']:+.1f}", 
                           f"{s['Rent_Score']-avg_scores['Rent_Score']:+.1f}", f"{s['Store_Score']-avg_scores['Store_Score']:+.1f}", f"{s['Vacancy_Score']-avg_scores['Vacancy_Score']:+.1f}"]
            }))

        st.markdown("---")
        st.subheader("📊 전체 상권 지표 분포 (Stacked View)")
        # Stacked Bar Chart
        plot_df = df.copy()
        
        fig_stacked = px.bar(df, x='상권_코드_명', 
                             y=['Sales_Score', 'Pop_Score', 'Trend_Score'],
                             title="가점 지표 상세 (수요/관심도)",
                             labels={'value': 'Score', 'variable': 'Category', '상권_코드_명': '상권명'},
                             barmode='group')
        st.plotly_chart(fig_stacked, use_container_width=True)
        
        st.subheader("📉 비용 및 리스크 요인 비교")
        fig_risk = px.line(plot_df.sort_values('Coffee_Index', ascending=False), 
                           x='상권_코드_명', y=['Rent_Score', 'Store_Score', 'Vacancy_Score'],
                           markers=True, title="감점 지표 상세 (비용/경쟁)")
        st.plotly_chart(fig_risk, use_container_width=True)
        
        st.subheader("📋 전체 데이터 시트")
        st.dataframe(df.sort_values('Coffee_Index', ascending=False).style.background_gradient(cmap='YlOrRd'))

elif page == "4. 공간 분석 (GIS Map)":
    st.header("4. 위치 기반 포화도 및 밀집도 (Map)")
    
    tab1, tab2 = st.tabs(["🗺️ 상권 밀집도 지도", "📊 포화도 분석 (Saturation)"])
    
    with tab1:
        st.markdown("#### 서울시 전체 상권 대비 Hidden Gems 위치")
        if not df_full_geo.empty and '위도' in df_full_geo.columns and '경도' in df_full_geo.columns:
            df_map = df_full_geo.dropna(subset=['위도', '경도']).copy()
            df_map['Color'] = df_map['Is_Target'].map({True: 'Target', False: 'Other'})
            
            fig_map = px.scatter_mapbox(
                df_map, lat="위도", lon="경도", size="총_점포수", color="Color",
                hover_name="상권명", color_discrete_map={'Target': 'red', 'Other': 'gray'},
                zoom=10, height=600, mapbox_style="carto-positron"
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("📍 지도 데이터(위도/경도)를 불러올 수 없습니다. 'a_confirmed' 폴더의 좌표 밀집도 데이터 파일을 확인해주세요.")
        
    with tab2:
        st.subheader("포화도 분석 (매출 대비 점포수)")
        st.markdown("우하단(매출 높음, 점포수 적음)에 위치할수록 **기반 수요는 탄탄하나 경쟁이 낮은** 우량 상권입니다.")
        fig_sat = px.scatter(df, x='Sales_Score', y='Store_Score', size='Coffee_Index',
                             color='Coffee_Index', text='상권_코드_명',
                             labels={'Sales_Score': '매출 점수', 'Store_Score': '점포수 리스크'},
                             color_continuous_scale='RdYlGn_r')
        fig_sat.add_shape(type="line", x0=0, y0=0, x1=100, y1=100, line=dict(color="Gray", dash="dash"))
        st.plotly_chart(fig_sat, use_container_width=True)

elif page == "5. 인사이트 및 전략":
    st.header("5. 분석 인사이트 및 액션 플랜")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💡 주요 인사이트")
        st.markdown("""
        - **"온라인 트렌드의 영향"**: 서울대입구, 성신여대가 네이버 검색량 결합 후 순위가 급상승함. 이는 2030 세대의 높은 관심도로 인한 **미래 성장 채력**을 의미함.
        - **"화려한 매출의 함정"**: 점포수(경쟁)와 임대료(비용) 페널티 적용 시, 강남권 초대형 상권들의 지수가 대폭 하락하여 실질 수익성이 낮음을 시사함.
        """)
    with col2:
        st.subheader("🚀 상권별 액션 플랜")
        st.markdown("""
        - **양재역 (안정형)**: 직장인 픽업 겨냥 고회전 테이크아웃 모델 추천
        - **성신여대 (트렌드형)**: 바이럴 특화 SNS 감성 카페 및 고단가 디저트 전략
        - **구의/망원 (로컬형)**: 낮은 고정비 기반 로컬 커뮤니티형 소규모 카페
        """)

elif page == "6. 검증 가설 및 결론":
    st.header("6. 검증 가설 및 향후 과제")
    
    st.markdown("""
    <div class="report-text">
    <strong>검증할 수 있는 가설 (Testable Hypotheses)</strong>
    <ol>
        <li><strong>모멘텀 지연 가설</strong>: Trend Index가 3주 이상 상승 시, 1~2분기 뒤 실제 매출 상승 여부</li>
        <li><strong>비용 한계 가설</strong>: 임대가격지수 80 이상 지역의 1년 이내 폐업률 상관관계</li>
        <li><strong>유동인구 디커플링</strong>: 통과형 유동인구 비중과 실제 결제 전환율의 상관관계</li>
    </ol>
    
    <strong>결론</strong>: 본 분석은 단순 오프라인 데이터를 넘어 <strong>온라인 관심도(Trend)</strong>를 결합함으로써, 
    공급 과잉 시대에 실질적인 생존 확률이 높은 '대안 상권'을 제안하는 데 성공하였습니다.
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption("Data Source: 서울시 상권분석, 부동산원, Naver")
