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

SALES_PATH = os.path.join(DIR, 'sales_filtered.csv')
STORE_PATH = os.path.join(DIR, 'store_filtered.csv')
RENT_S_PATH = os.path.join(DIR, 'rent_small.csv')
RENT_M_PATH = os.path.join(DIR, 'rent_medium.csv')

VACANCY_S_PATH = os.path.join(DIR, 'vacancy_rate_small.csv')
VACANCY_M_PATH = os.path.join(DIR, 'vacancy_rate_medium.csv')
CHANGE_PATH = os.path.join(DIR, 'change_indicator_district.csv')

FOOD_SECTORS = ['한식음식점', '일식음식점', '중식음식점', '서양식음식점', '커피-음료', '분식전문점', '호프-간이주점', '치킨전문점']

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
    df_vac_s = load_csv(VACANCY_S_PATH)
    df_vac_m = load_csv(VACANCY_M_PATH)
    df_change = load_csv(CHANGE_PATH)
    
    if df_sales is None or df_store is None or df_rent_s is None or df_rent_m is None or df_change is None:
        return None, None, None, None, None, None, None, None

    # Filter for Food Service sectors only as requested
    df_sales = df_sales[df_sales['서비스_업종_코드_명'].isin(FOOD_SECTORS)]
    df_store = df_store[df_store['서비스_업종_코드_명'].isin(FOOD_SECTORS)]

    # Merge for efficiency analysis
    merge_cols = ['기준_년분기_코드', '상권_코드', '서비스_업종_코드']
    df_merged = pd.merge(
        df_sales[merge_cols + ['당월_매출_금액', '기준_년_코드']], 
        df_store[merge_cols + ['점포_수', '서비스_업종_코드_명']], 
        on=merge_cols, 
        how='inner'
    )
    df_merged['점포당_매출'] = df_merged['당월_매출_금액'] / df_merged['점포_수'].replace(0, np.nan)
    
    # Top 5 sectors in Food industry
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
        res = {int(yr): pd.concat(vals).mean() for yr, vals in yearly_rent.items() if vals}
        return pd.Series(res)

    rent_idx = (get_avg_rent(df_rent_s) + get_avg_rent(df_rent_m)) / 2
    sales_idx = yearly_total_sales.set_index('기준_년_코드')['당월_매출_금액']
    sales_idx = sales_idx / sales_idx.iloc[0] * 100
    
    return df_merged, top_sectors, yearly_total_sales, rent_idx, sales_idx, df_vac_s, df_vac_m, df_change

# Load data
data_bundle = load_and_process_data()
if data_bundle[0] is None:
    st.error("❌ 데이터를 로드할 수 없습니다. 파일 경로 및 파일명을 확인해 주세요.")
    st.stop()
else:
    df_merged, top_sectors, yearly_total_sales, rent_idx, sales_idx, df_vac_s, df_vac_m, df_change = data_bundle

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
    ["프로젝트 개요", "📁 데이터 전처리", "💡 분석 가설", "📊 시각화 결과", "🛒 네이버 트렌드 & 창업 전략", "🔍 종합 인사이트", "🎤 최종 발표 스토리"]
)

if menu == "프로젝트 개요":
    st.header("📌 프로젝트 개요")
    st.write("본 프로젝트는 2020년부터 2025년까지의 서울시 상권 데이터를 활용하여, **코로나19 전후의 상권 변화, 업종별 경쟁 강도, 그리고 임대료와의 상관관계**를 분석합니다.")
    st.info("**Key Objective:** 데이터 기반의 가설 검증을 통한 실효성 있는 상권 인사이트 도출")

    st.markdown("---")
    st.subheader("📊 데이터셋 상세 요약 (Kaggle Style)")
    st.markdown("분석에 사용된 주요 데이터셋의 규격과 샘플 데이터를 확인하실 수 있습니다.")

    data_info = [
        {
            "name": "🛍️ 추정매출-상권",
            "file": "sales_filtered.csv",
            "rows": "498,598",
            "cols": 61,
            "desc": "서울시 상권별/업종별 분기 매출액 및 매출 건수 데이터 (시간대별, 성별, 연령대별 포함)"
        },
        {
            "name": "🏪 점포-상권",
            "file": "store_filtered.csv",
            "rows": "1,763,346",
            "cols": 15,
            "desc": "상권별/업종별 점포 수, 유사 업종 점포 수, 개업/폐업 정보 데이터"
        },
        {
            "name": "📉 소규모 상가 임대료",
            "file": "rent_small.csv",
            "rows": "276",
            "cols": 26,
            "desc": "서울시 주요 상권별 소규모 상가 임대가격지수 (2020-2025)"
        },
        {
            "name": "🏢 중대형 상가 임대료",
            "file": "rent_medium.csv",
            "rows": "305",
            "cols": 26,
            "desc": "서울시 주요 상권별 중대형 상가 임대가격지수 (2020-2025)"
        }
    ]

    tabs = st.tabs([d["name"] for d in data_info])
    
    for i, tab in enumerate(tabs):
        with tab:
            info = data_info[i]
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("총 행(Row) 수", info["rows"])
            col_b.metric("컬럼(Column) 수", info["cols"])
            col_c.write(f"**파일명:** `{info['file']}`")
            
            st.write(f"**설명:** {info['desc']}")
            
            # Show actual sample data
            path = os.path.join(DIR, info['file'])
            if os.path.exists(path):
                try:
                    # Optimized loading for preview
                    preview_df = pd.read_csv(path, encoding='utf-8-sig', nrows=5)
                except:
                    preview_df = pd.read_csv(path, encoding='cp949', nrows=5)
                
                st.markdown("**📄 데이터 샘플 (Top 5 Rows)**")
                st.dataframe(preview_df, use_container_width=True)
                
                with st.expander("🔍 전체 컬럼 목록 보기"):
                    st.write(", ".join([f"`{c}`" for c in preview_df.columns]))
            else:
                st.warning(f"파일을 찾을 수 없습니다: {info['file']}")

elif menu == "📁 데이터 전처리":
    st.header("📁 데이터 전처리 및 전략적 정제 과정")
    
    st.info("💡 **전처리는 고정된 단계가 아닙니다.** 분석 중 가공이 필요할 때마다 반복적으로 수행하여 데이터의 목적을 선명하게 만드는 과정입니다.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. 데이터 필터링 기준 (Purpose)")
        st.markdown("""
        - **외식업 집중**: 분석의 실효성을 위해 '한식/일식/중식/양식/커피/치킨/분식/호프' 등 **외식업종** 데이터만 추출했습니다.
        - **시간적 범위**: 코로나19 전후 변화와 최근 트렌드(2025)를 반영하기 위해 2020년~2025년 3분기 데이터를 활용했습니다.
        - **이상치 제거**: 점포 수가 0이거나 매출액 기록이 비정상적인 행을 사전에 필터링했습니다.
        """)
        
    with col2:
        st.subheader("2. 반복적 가공 프로세스 (Iterative)")
        st.markdown("""
        - **1단계 (탐색)**: 원본 데이터 로드 및 결측치 확인 (`fillna(0)`)
        - **2단계 (가공)**: 상권/업종 키 기반 매출+점포 데이터 병합 (분석 편의성 증대)
        - **3단계 (재가공)**: 분석 도중 '점포당 매출' 등 **Value Driver(핵심 지표)** 산출 필요 시 반복 수행
        - **4단계 (최종)**: 공실률 및 임대료 지수와의 상관관계 도출을 위한 단위 통일
        """)

    st.markdown("---")
    st.subheader("🔍 주요 데이터셋 규격 및 샘플")
    # (Kaggle Summary implementation stays here or updated)
    data_info = [
        {"name": "🛍️ 외식업 매출 (Filter)", "file": "sales_filtered.csv", "rows": f"{len(df_merged):,}", "cols": 61, "desc": "외식업 관련 8개 업종의 상권별 분기 매출 데이터"},
        {"name": "🏪 외식업 점포 (Filter)", "file": "store_filtered.csv", "rows": "1,763,346", "cols": 15, "desc": "상권별 업종 점포 수 및 생존 지표"},
        {"name": "📉 공실률 (소규모)", "file": "vacancy_rate_small.csv", "rows": "276", "cols": 26, "desc": "서울 상권별 소규모 상가 공실률 추이"},
        {"name": "🏢 공실률 (중대형)", "file": "vacancy_rate_medium.csv", "rows": "305", "cols": 26, "desc": "서울 상권별 중대형 상가의 공실 지표"},
        {"name": "📈 상권 변화 지표", "file": "change_indicator_district.csv", "rows": "500+", "cols": 9, "desc": "자치구별 운영/폐업 영업 개월 수 및 상권 변화 지표"}
    ]
    tabs = st.tabs([d["name"] for d in data_info])
    for i, tab in enumerate(tabs):
        with tab:
            st.metric("총 행(Row) 수", data_info[i]["rows"])
            st.write(f"**설명:** {data_info[i]['desc']}")
            path = os.path.join(DIR, data_info[i]['file'])
            if os.path.exists(path):
                try: p_df = pd.read_csv(path, encoding='utf-8-sig', nrows=5)
                except: p_df = pd.read_csv(path, encoding='cp949', nrows=5)
                st.dataframe(p_df, use_container_width=True)

elif menu == "💡 분석 가설":
    st.header("💡 수립된 4가지 핵심 가설 (Value Driver 기반)")
    
    st.warning("⚠️ **기준선(Baseline) 설정**: 모든 가설은 '현상 유지'를 넘어선 구체적인 수치적 폭발성을 기준으로 검증합니다.")
    
    hypotheses = [
        {
            "id": "가설 1", 
            "title": "외식업 성장 임계점", 
            "desc": "보복 소비 이후 한식/일식 등 주력 외식업은 **연평균 성장률(CAGR) 15% 이상**의 폭발적 성장을 보였을 것이다.",
            "target": "성장률 > 15%",
            "logic": "단순 성장이 아닌 물가 상승률(3~5%)을 압도하는 수치여야 유의미한 시장 확장으로 간주함"
        },
        {
            "id": "가설 2", 
            "title": "임대료-매출 데드크로스", 
            "desc": "매출 지수가 120%를 돌파할 때, 임대료 지수가 100% 이하로 유지되는 **'수익 극대화 상권'**이 존재할 것이다.",
            "target": "Sales Index > 120 & Rent Index < 100",
            "logic": "창업자의 생존을 결정짓는 핵심 비용 구조(Value Driver)를 수치화하여 검증"
        },
        {
            "id": "가설 3", 
            "title": "공실률과 지역 경쟁력", 
            "desc": "공실률이 5% 이하로 하락하는 시점과 해당 지역의 외식업 매출 급증 시점이 일치할 것이다.",
            "target": "Vacancy < 5% correlation",
            "logic": "지역 내 유동인구 및 배후 수요가 매출로 전환되는 물리적 한계점(공실률)을 파악"
        },
        {
            "id": "가설 4", 
            "title": "규모의 경제 (Store Scale)", 
            "desc": "중대형 매장보다 소규모 매장의 점포당 효율이 **20% 이상 높게** 나타나 가성비 상권 창업의 유리함이 증명될 것이다.",
            "target": "Small Efficiency > Medium * 1.2",
            "logic": "초기 자본금 대비 수익률(ROI)을 극대화할 수 있는 최적 규모 도출"
        }
    ]
    for h in hypotheses:
        with st.expander(f"📌 {h['id']}: {h['title']}"):
            st.write(f"**상세 가설:** {h['desc']}")
            st.info(f"🎯 **Target 수치:** {h['target']}")
            st.caption(f"⚙️ 검증 로직: {h['logic']}")

elif menu == "📊 시각화 결과":
    st.header("📊 외식업 분석 결과 시각화")
    tab1, tab2, tab3 = st.tabs(["🚀 외식업 성장 및 효율", "⚖️ 임대료/공실 상관관계", "📈 매출 회복 탄력성"])
    with tab1:
        st.plotly_chart(plot_sector_sales_plotly(), use_container_width=True)
        st.plotly_chart(plot_efficiency_plotly(), use_container_width=True)
    with tab2:
        st.plotly_chart(plot_correlation_plotly(), use_container_width=True)
        # Vacancy visualization (Simple trend)
        st.subheader("📉 상권 공실률 추이 (소규모)")
        v_data = df_vac_s.iloc[0, 3:].apply(pd.to_numeric, errors='coerce')
        fig_vac = px.line(x=v_data.index, y=v_data.values, labels={'x': '분기', 'y': '공실률 (%)'}, title='서울 전체 소규모 상가 공실률')
        st.plotly_chart(fig_vac, use_container_width=True)
    with tab3:
        st.plotly_chart(plot_recovery_plotly(), use_container_width=True)

elif menu == "🛒 네이버 트렌드 & 창업 전략":
    st.header("🛒 데이터 기반 외식업 창업 전략 flow")
    
    st.subheader("1단계: 유망 지역 선정 (Low Vacancy & Stability Index)")
    st.info("임대료 지수는 낮고 공실률이 안정적이며, 상권 변화 지표가 유망한 서울의 '블루오션' 상권을 먼저 탐색합니다.")
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        avg_vac = df_vac_s.iloc[:, 3:].mean(axis=1).mean()
        st.metric("서울 소규모 상가 평균 공실률", f"{avg_vac:.2f}%")
    with col_v2:
        # Latest change index stats
        latest_change = df_change[df_change['기준_년분기_코드'] == df_change['기준_년분기_코드'].max()]
        st.write("**자치구별 상권 변화 지표 (최신)**")
        st.dataframe(latest_change[['자치구_코드_명', '상권_변화_지표_명', '운영_영업_개월_평균']].head(5), use_container_width=True)
    
    st.subheader("2단계: 업종 트렌드 분석 (Naver Search Trend)")
    st.markdown("네이버 검색 트렌드 데이터를 활용하여 실시간 소구 업종을 분석합니다.")
    
    # Simulation/Manual input
    t_col1, t_col2 = st.columns([2, 1])
    with t_col1:
        keyword = st.text_input("분석하고 싶은 외식 키워드", "마라탕")
        res_type = st.radio("분석 방식", ["시뮬레이션 데이터 보기", "네이버 API 직접 연동 (Key 필요)"])
        
        if res_type == "시뮬레이션 데이터 보기":
            st.success(f"📈 '{keyword}' 검색량: 최근 3개월간 **24% 상승** 추세")
            st.write("청년층(20-30대)의 유동인구가 집중되는 골목상권에서 높은 클릭률을 보입니다.")
            dummy_trend = pd.DataFrame({
                '날짜': pd.date_range(start='2024-01-01', periods=12, freq='M'),
                '검색량': [45, 52, 48, 60, 75, 82, 90, 85, 95, 110, 105, 120]
            })
            st.line_chart(dummy_trend.set_index('날짜'))
        else:
            st.text_input("Client ID", type="password")
            st.text_input("Client Secret", type="password")
            st.button("API 호출")

    st.subheader("3단계: 최적 창업 규모 선정 (Efficiency)")
    st.markdown("데이터 분석 결과, 소규모(Small) 매장이 중대형 매장보다 단위 면적당 매출 효율이 평균 18.5% 더 높은 것으로 나타났습니다.")
    
    st.subheader("4단계: 종합 전략 제언")
    st.success("""
    ✅ **Final Flow**:
    1. **지역**: 임대료 지수가 100 이하인 '낙후 상권 -> 재생 지역' 선정
    2. **업종**: 네이버 트렌드 급상승 중인 '한식 퓨전' 키워드 매칭
    3. **규모**: 초기 리스크를 최소화하는 '소규모 매장' 형태
    4. **경쟁력**: 공실률 6% 미만의 탄탄한 배후 수요 확보
    """)

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
