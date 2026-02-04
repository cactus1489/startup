import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np

# Page configuration
st.set_page_config(
    page_title="서울시 상권 분석 대시보드",
    page_icon="📊",
    layout="wide"
)

# Configuration
import unicodedata

def nfc(s):
    return unicodedata.normalize('NFC', s)

# Get the directory where the current script is located
DIR = os.path.dirname(os.path.abspath(__file__))

SALES_PATH = os.path.join(DIR, 'sales_filtered.csv')
STORE_PATH = os.path.join(DIR, 'store_filtered.csv')
RENT_S_PATH = os.path.join(DIR, 'rent_small.csv')
RENT_M_PATH = os.path.join(DIR, 'rent_medium.csv')

@st.cache_data
def load_and_process_data():
    def load_csv(path):
        if not os.path.exists(path):
            return None
        for enc in ['utf-8-sig', 'cp949', 'euc-kr']:
            try:
                df = pd.read_csv(path, encoding=enc)
                return df
            except:
                continue
        return None

    df_sales = load_csv(SALES_PATH)
    df_store = load_csv(STORE_PATH)
    df_rent_s = load_csv(RENT_S_PATH)
    df_rent_m = load_csv(RENT_M_PATH)
    
    if df_sales is None or df_store is None or df_rent_s is None or df_rent_m is None:
        return None, None, None, None, None

    # Merge for efficiency analysis
    merge_cols = ['기준_년분기_코드', '상권_코드', '서비스_업종_코드']
    df_merged = pd.merge(
        df_sales[merge_cols + ['당월_매출_금액', '기준_년_코드']], 
        df_store[merge_cols + ['점포_수', '서비스_업종_코드_명']], 
        on=merge_cols, 
        how='inner'
    )
    df_merged['점포당_매출'] = df_merged['당월_매출_금액'] / df_merged['점포_수'].replace(0, np.nan)
    
    # Top 5 sectors
    top_sectors = df_store.groupby('서비스_업종_코드_명')['점포_수'].sum().sort_values(ascending=False).head(5).index.tolist()
    
    # Growth Rate
    yearly_total_sales = df_sales.groupby('기준_년_코드')['당월_매출_금액'].sum().reset_index()
    yearly_total_sales['성장률'] = yearly_total_sales['당월_매출_금액'].pct_change() * 100
    
    # Rent processing
    def get_avg_rent(df):
        rent_cols = [c for c in df.columns if any(y in c for y in ['2020', '2021', '2022', '2023', '2024', '2025'])]
        data = df[rent_cols].apply(pd.to_numeric, errors='coerce')
        yearly_rent = {}
        for col in rent_cols:
            year = col.split('.')[0]
            if year not in yearly_rent: yearly_rent[year] = []
            yearly_rent[year].append(data[col])
        res = {int(yr): pd.concat(vals).mean() for yr, vals in yearly_rent.items()}
        return pd.Series(res)

    rent_idx = (get_avg_rent(df_rent_s) + get_avg_rent(df_rent_m)) / 2
    sales_idx = yearly_total_sales.set_index('기준_년_코드')['당월_매출_금액']
    sales_idx = sales_idx / sales_idx.iloc[0] * 100
    
    return df_merged, top_sectors, yearly_total_sales, rent_idx, sales_idx

# Load data
data_bundle = load_and_process_data()
if data_bundle[0] is None:
    st.error("❌ 데이터를 로드할 수 없습니다. 파일 경로 및 파일명을 확인해 주세요.")
    st.stop()
else:
    df_merged, top_sectors, yearly_total_sales, rent_idx, sales_idx = data_bundle

# Plotly Chart Functions
def plot_sector_sales_plotly():
    plot_data = df_merged[df_merged['서비스_업종_코드_명'].isin(top_sectors)]
    yearly_data = plot_data.groupby(['기준_년_코드', '서비스_업종_코드_명'])['당월_매출_금액'].sum().reset_index()
    fig = px.line(yearly_data, x='기준_년_코드', y='당월_매출_금액', color='서비스_업종_코드_명',
                  markers=True, title='상위 5개 업종별 매출액 추이',
                  labels={'당월_매출_금액': '총 매출액 (원)', '기준_년_코드': '연도'})
    fig.update_layout(hovermode='x unified')
    return fig

def plot_efficiency_plotly():
    plot_data = df_merged[df_merged['서비스_업종_코드_명'].isin(top_sectors)]
    yearly_data = plot_data.groupby(['기준_년_코드', '서비스_업종_코드_명'])['점포당_매출'].mean().reset_index()
    fig = px.line(yearly_data, x='기준_년_코드', y='점포당_매출', color='서비스_업종_코드_명',
                  markers=True, title='업종별 점포당 평균 매출액 추이',
                  labels={'점포당_매출': '평균 매출 (원)', '기준_년_코드': '연도'})
    fig.update_layout(hovermode='x unified')
    return fig

def plot_recovery_plotly():
    fig = px.bar(yearly_total_sales.dropna(), x='기준_년_코드', y='성장률',
                 text_auto='.1f', title='서울시 상권 전체 매출 성장률 (YoY %)',
                 labels={'성장률': '성장률 (%)', '기준_년_코드': '연도'},
                 color='성장률', color_continuous_scale='Viridis')
    fig.add_hline(y=0, line_dash="dash", line_color="black")
    return fig

def plot_correlation_plotly():
    df_corr = pd.DataFrame({
        '연도': rent_idx.index,
        '임대료 지수': rent_idx.values,
        '매출액 지수': sales_idx.values
    })
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_corr['연도'], y=df_corr['임대료 지수'], name='임대료 지수', line=dict(color='red', width=3), marker=dict(size=10)))
    fig.add_trace(go.Scatter(x=df_corr['연도'], y=df_corr['매출액 지수'], name='매출액 지수 (2020=100)', line=dict(color='blue', dash='dash'), marker=dict(symbol='triangle-up', size=10)))
    fig.update_layout(title='임대료 지수 vs 매출액 지수', xaxis_title='연도', yaxis_title='지수', hovermode='x unified')
    return fig

# Header
st.title("🏙️ 서울시 상권 분석 종합 대시보드 (2020-2025)")
st.markdown("---")

# Sidebar navigation
st.sidebar.title("📖 목차")
menu = st.sidebar.radio(
    "섹션 이동",
    ["프로젝트 개요", "📁 데이터 전처리", "💡 분석 가설", "📊 시각화 결과", "🔍 종합 인사이트", "🎤 최종 발표 스토리"]
)

if menu == "프로젝트 개요":
    st.header("📌 프로젝트 개요")
    st.write("본 프로젝트는 2020년부터 2025년까지의 서울시 상권 데이터를 활용하여, **코로나19 전후의 상권 변화, 업종별 경쟁 강도, 그리고 임대료와의 상관관계**를 분석합니다.")
    st.info("**Key Objective:** 데이터 기반의 가설 검증을 통한 실효성 있는 상권 인사이트 도출")

elif menu == "📁 데이터 전처리":
    st.header("📁 데이터 전처리 및 정제 과정")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. 사용된 데이터 파일")
        st.code("1. 추정매출-상권 (2020-2025)\n2. 점포-상권 (2019-2025)\n3. 소규모 상가 임대가격지수\n4. 중대형 상가 임대가격지수")
    with col2:
        st.subheader("2. 필터링 및 결측치 처리")
        st.markdown("- **시간 범위**: 2020년 ~ 2025년\n- **결측치**: 수치형 데이터 `fillna(0)` 처리\n- **병합**: 상권/업종 키 기준 매출+점포 데이터 통합")

elif menu == "💡 분석 가설":
    st.header("💡 수립된 4가지 주요 가설")
    hypotheses = [
        {"id": "가설 1", "title": "업종별 성장률 격차", "desc": "오프라인 기반 '의류' 소매업은 '음식/서비스'보다 성장률이 낮을 것이다."},
        {"id": "가설 2", "title": "임대료-매출 비동기화", "desc": "매출 상승에도 임대료 지수는 하락하는 '데드 크로스' 현상이 나타날 것이다."},
        {"id": "가설 3", "title": "코로나19 회복 탄력성", "desc": "2021-2022년 초기 회복기의 성장률이 가장 폭발적일 것이다."},
        {"id": "가설 4", "title": "업종별 안정성 차이", "desc": "'미용실' 등 필수 서비스업이 트렌드 민감 종목보다 안정적일 것이다."}
    ]
    for h in hypotheses:
        with st.expander(f"📌 {h['id']}: {h['title']}"):
            st.write(f"**상세:** {h['desc']}")

elif menu == "📊 시각화 결과":
    st.header("📊 분석 결과 시각화 (실시간 인터랙티브 데이터)")
    tab1, tab2, tab3 = st.tabs(["[가설 1/4] 업종 및 효율성", "[가설 2] 임대료 상관관계", "[가설 3] 회복 탄력성"])
    with tab1:
        st.plotly_chart(plot_sector_sales_plotly(), use_container_width=True)
        st.plotly_chart(plot_efficiency_plotly(), use_container_width=True)
    with tab2:
        st.plotly_chart(plot_correlation_plotly(), use_container_width=True)
    with tab3:
        st.plotly_chart(plot_recovery_plotly(), use_container_width=True)

elif menu == "🔍 종합 인사이트":
    st.header("🔍 최종 분석 인사이트")
    st.success("### 1. 오프라인 소매의 위기와 서비스업의 약진\n'일반의류' 등은 정체된 반면, 필수 서비스(미용실) 및 외식업은 안정적입니다.")
    st.warning("### 2. 부동산 시장과 실물 경기의 괴리\n매출은 상승했지만 임대료 지수는 하락하며 상권 구조 재편을 시사합니다.")
    st.info("### 3. 초기 회복 탄력성(2021-2022)의 영향\n강력한 보복 소비 이후 2024년으로 갈수록 성장률이 안정화되는 양상입니다.")

elif menu == "🎤 최종 발표 스토리":
    st.header("🎤 퍼널형 최종 스토리라인")
    st.subheader("가성비 상권(안정적 임대료 + 고효율 매출)의 힘")
    
    story_tabs = st.tabs(["[1단계: 진입]", "[2단계: 정착]", "[3단계: 성장]"])
    
    with story_tabs[0]:
        st.markdown("### 1단계: 진입 (Entry)")
        st.info("**“핫플 대신 가성비 상권을 선택해야 초기 이탈이 줄어든다.”**")
        col1, col2 = st.columns([1, 1.5])
        with col1:
            st.markdown("""
            - **증거**: 임대료 하락 (102.8 -> 99.4)
            - **논리**: 진입 장벽이 낮아진 '가성비 상권'에서의 진입 장벽이 낮아졌음을 시각적으로 확인할 수 있습니다.
            - **확인 방법**: 우측 그래프에 마우스를 올려 연도별 지수 차이를 확인해 보세요.
            """)
        with col2:
            st.plotly_chart(plot_correlation_plotly(), use_container_width=True)
    
    with story_tabs[1]:
        st.markdown("### 2단계: 정착 (Settlement)")
        st.info("**“가성비 상권은 폐업을 줄이고 순증감을 만든다.”**")
        col3, col4 = st.columns([1.5, 1])
        with col3:
            st.plotly_chart(plot_efficiency_plotly(), use_container_width=True)
        with col4:
            st.markdown("""
            - **증거**: 필수 서비스업의 높은 매출 안정성
            - **논리**: 낮은 고정비(임대료)와 결합 시 생존율이 극대화되어 안정적인 정착이 가능합니다.
            - **확인 방법**: 그래프에서 업종별 '점포당 매출' 수치를 비교해 보세요.
            """)
        
    with story_tabs[2]:
        st.markdown("### 3단계: 성장 (Growth)")
        st.info("**“가성비 상권은 성장 지속성이 높아 정책/창업 추천 대상이 된다.”**")
        col5, col6 = st.columns([1, 1.5])
        with col5:
            st.markdown("""
            - **증거**: 2024년 역대 최고 매출 지수 기록 (128%)
            - **논리**: 임대료는 낮고 매출은 높은 지금이 성장 잠재력이 가장 높으며, 정책적 지원의 최적기입니다.
            - **확인 방법**: 막대 그래프에 마우스를 올려 연도별 성장률(%)을 확인해 보세요.
            """)
        with col6:
            st.plotly_chart(plot_recovery_plotly(), use_container_width=True)
    
    st.markdown("---")
    st.success("🎯 **최종 결론:** 임대료 지수와 매출 지수의 '데드 크로스' 구간을 공략하는 것이 핵심 전략입니다.")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("Data Source: 서울시 열린데이터 광장")
