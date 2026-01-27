import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import csv

# 설정
st.set_page_config(page_title="Naver API 데이터 분석 대시보드", layout="wide")

# .env 로드
load_dotenv()
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 카테고리 매핑
CATEGORIES = {
    "식품": "50000007",
    "패션의류": "50000000",
    "화장품/미용": "50000003",
    "디지털/가전": "50000004",
    "가구/인테리어": "50000005",
    "출산/육아": "50000006",
    "스포츠/레저": "50000008",
    "생활/건강": "50000002"
}

# CSS 커스텀
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 데이터 수집 함수 (기존 collect_data.py 로직 활용)
def get_headers():
    return {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "Content-Type": "application/json"
    }

def fetch_shopping_insight(keyword, category_id, start_date, end_date):
    """네이버 쇼핑인사이트 키워드 클릭 트렌드 조회 (카테고리별)"""
    url = "https://openapi.naver.com/v1/datalab/shopping/category/keywords"
    body = {
        "startDate": start_date.strftime("%Y-%m-%d"),
        "endDate": end_date.strftime("%Y-%m-%d"),
        "timeUnit": "date",
        "category": category_id,
        "keyword": [{"name": keyword, "param": [keyword]}]
    }
    res = requests.post(url, headers=get_headers(), data=json.dumps(body))
    if res.status_code == 200:
        results = res.json().get('results', [])
        if results and results[0].get('data'):
            return results[0]['data']
    return []

def fetch_search_trend(keyword, start_date, end_date):
    """네이버 통합검색 트렌드 조회 (일반 검색어 기반)"""
    url = "https://openapi.naver.com/v1/datalab/search"
    body = {
        "startDate": start_date.strftime("%Y-%m-%d"),
        "endDate": end_date.strftime("%Y-%m-%d"),
        "timeUnit": "date",
        "keywordGroups": [{"groupName": keyword, "keywords": [keyword]}]
    }
    res = requests.post(url, headers=get_headers(), data=json.dumps(body))
    if res.status_code == 200:
        results = res.json().get('results', [])
        if results and results[0].get('data'):
            return results[0]['data']
    return []

def fetch_shopping(keyword):
    url = f"https://openapi.naver.com/v1/search/shop.json?query={keyword}&display=50"
    res = requests.get(url, headers=get_headers())
    if res.status_code == 200:
        return res.json().get('items', [])
    return []

def fetch_blog(keyword):
    url = f"https://openapi.naver.com/v1/search/blog.json?query={keyword}&display=50"
    res = requests.get(url, headers=get_headers())
    if res.status_code == 200:
        return res.json().get('items', [])
    return []

# 사이드바
st.sidebar.title("📊 검색 설정")
category_name = st.sidebar.selectbox("검색 대상 카테고리", list(CATEGORIES.keys()))
category_id = CATEGORIES[category_name]
keywords_input = st.sidebar.text_input("키워드 입력 (쉼표로 구분)", "오메가3, 비타민d, 유산균, 루테인, 밀크씨슬, 콜라겐, 마그네슘")
date_range = st.sidebar.date_input("조회 기간", [datetime(2025, 1, 1), datetime(2025, 12, 31)])

# 날짜 입력 유효성 검사
if len(date_range) != 2:
    st.sidebar.warning("시작일과 종료일을 모두 선택해주세요.")
    run_btn = False
else:
    run_btn = st.sidebar.button("데이터 분석 실행")

if run_btn:
    if not CLIENT_ID or not CLIENT_SECRET:
        st.error(".env 파일에 NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET을 설정해주세요.")
    else:
        keywords = [k.strip() for k in keywords_input.split(",")]
        
        with st.spinner("데이터를 수집하고 분석 중입니다..."):
            all_trends = []
            all_shopping = {}
            all_blogs = {}
            
            for kw in keywords:
                # 1. 트렌드 데이터 수집 (쇼핑 인사이트 우선, 부족 시 일반 검색 트렌드로 보충)
                st.write(f"🔍 '{kw}' 트렌드 수집 중...")
                trend_data = fetch_shopping_insight(kw, category_id, date_range[0], date_range[1])
                
                if not trend_data:
                    st.info(f"'{kw}' 쇼핑 데이터가 부족하여 검색 트렌드 데이터로 대체합니다.")
                    trend_data = fetch_search_trend(kw, date_range[0], date_range[1])
                
                if trend_data:
                    for td in trend_data:
                        td['keyword'] = kw
                    all_trends.extend(trend_data)
                
                # 2. 쇼핑 상품 데이터 수집
                all_shopping[kw] = fetch_shopping(kw)
                
                # 3. 블로그 콘텐츠 데이터 수집
                all_blogs[kw] = fetch_blog(kw)
            
            # DataFrame 변환 및 전처리
            if all_trends:
                df_trend = pd.DataFrame(all_trends)
                df_trend['period'] = pd.to_datetime(df_trend['period'])
                df_trend['month'] = df_trend['period'].dt.month
                df_trend['day_of_week'] = df_trend['period'].dt.day_name()
            else:
                df_trend = pd.DataFrame()
            
            # 메인 화면 - 탭 구성
            tab1, tab2, tab3, tab4 = st.tabs(["📈 트랜드 분석", "🛒 쇼핑 EDA", "📝 콘텐츠 통계", "🗂️ Raw Data"])
            
            if not df_trend.empty:
                with tab1:
                    st.subheader("키워드별 검색 트렌드 비교")
                    # 1. 시계열 라인 차트 (Graph 1)
                    fig_line = px.line(df_trend, x="period", y="ratio", color="keyword", 
                                       title="2025년 일별 검색 추이",
                                       template="plotly_white")
                    st.plotly_chart(fig_line, use_container_width=True)
                    
                    col1_inner, col2_inner = st.columns(2)
                    with col1_inner:
                        # 2. 요일별 열지도 (Graph 2)
                        df_heat = df_trend.groupby(['keyword', 'day_of_week'])['ratio'].mean().reset_index()
                        fig_heat = px.density_heatmap(df_heat, x="day_of_week", y="keyword", z="ratio",
                                                     title="요일별 평균 검색 강도", color_continuous_scale="Viridis")
                        st.plotly_chart(fig_heat)

                    # 통계 요약표 (Table 1)
                    st.write("### 키워드별 통계 요약")
                    summary = df_trend.groupby('keyword')['ratio'].agg(['mean', 'max', 'min']).reset_index()
                    summary.columns = ['키워드', '평균', '최대', '최소']
                    st.table(summary)
                    
                    # 피크 데이터 (Table 2)
                    st.write("### 검색 피크(최고점) 발생일 분석")
                    peak_df = df_trend.sort_values('ratio', ascending=False).groupby('keyword').head(1).reset_index()
                    st.dataframe(peak_df[['keyword', 'period', 'ratio']])
            else:
                with tab1:
                    st.warning("데이터가 없어 트렌드 분석을 표시할 수 없습니다.")

            with tab2:
                st.subheader("쇼핑 데이터 상세 분석")
                # 모든 키워드 통합 쇼핑 데이터
                all_shop_list = []
                for k, items in all_shopping.items():
                    if items:
                        temp_df = pd.DataFrame(items)
                        temp_df['keyword'] = k
                        all_shop_list.append(temp_df)
                
                if all_shop_list:
                    df_all_shop = pd.concat(all_shop_list)
                    df_all_shop['lprice'] = pd.to_numeric(df_all_shop['lprice'])
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        # 3. 가격 분포 히스토그램 (Graph 3)
                        fig_hist = px.histogram(df_all_shop, x="lprice", color="keyword", barmode="overlay",
                                                title="가격대별 상품 분포 비교")
                        st.plotly_chart(fig_hist)
                    
                    with c2:
                        # 4. 판매처별 빈도 막대그래프 (Graph 4)
                        mall_counts = df_all_shop.groupby(['keyword', 'mallName']).size().reset_index(name='count')
                        fig_mall = px.bar(mall_counts.sort_values('count', ascending=False).head(20), 
                                          x="mallName", y="count", color="keyword", title="주요 판매처별 상품 수")
                        st.plotly_chart(fig_mall)

                    # 5. 브랜드 vs 가격 산점도 (Graph 5) - 브랜드 정보 활용
                    st.write("### 브랜드별 가격 분포 (산점도)")
                    fig_scatter = px.scatter(df_all_shop, x="brand", y="lprice", color="keyword", size="lprice",
                                             hover_data=['title'], title="브랜드별 가격대 분포 분석")
                    st.plotly_chart(fig_scatter, use_container_width=True)

                    c3, c4 = st.columns(2)
                    with c3:
                        # 6. 브랜드 점유율 (Graph 6)
                        brand_counts = df_all_shop[df_all_shop['brand'] != ''].groupby(['keyword', 'brand']).size().reset_index(name='count')
                        fig_brand = px.bar(brand_counts.sort_values('count', ascending=False).head(15), 
                                           x="count", y="brand", color="keyword", orientation='h',
                                           title="주요 브랜드 점유율 (Top 15)")
                        st.plotly_chart(fig_brand)
                    
                    with c4:
                        # 7. 카테고리 분포 (Graph 7)
                        cat_counts = df_all_shop.groupby('category3').size().reset_index(name='count')
                        fig_cat = px.pie(cat_counts, values='count', names='category3', 
                                         title="상품 카테고리 분포 (분류명 기준)", hole=0.4)
                        st.plotly_chart(fig_cat)

                    # 가격 통계표 (Table 3)
                    st.write("### 가격 통계 분석")
                    price_stats = df_all_shop.groupby('keyword')['lprice'].agg(['mean', 'median', 'min', 'max', 'count']).reset_index()
                    price_stats.columns = ['키워드', '평균가', '중앙값', '최저가', '최고가', '상품수']
                    st.table(price_stats)

                    # 상위 상품 리스트 (Table 4)
                    st.write("### 상위 검색 상품 상세 리스트 (Top 20)")
                    st.dataframe(df_all_shop[['keyword', 'title', 'lprice', 'mallName', 'brand', 'category3']].head(20))
            
            with tab3:
                st.subheader("블로그 콘텐츠 통계 및 오피니언 리스트")
                # 블로그 데이터 통합
                all_blog_list = []
                for k, items in all_blogs.items():
                    if items:
                        temp_df = pd.DataFrame(items)
                        temp_df['keyword'] = k
                        all_blog_list.append(temp_df)
                
                if all_blog_list:
                    df_all_blog = pd.concat(all_blog_list)
                    # 8. 블로그 작성일 분포 (Graph 8)
                    df_all_blog['postdate'] = pd.to_datetime(df_all_blog['postdate'], format='%Y%m%d', errors='coerce')
                    df_all_blog = df_all_blog.dropna(subset=['postdate'])
                    fig_blog = px.histogram(df_all_blog, x="postdate", color="keyword", title="블로그 작성일 시계열 분포")
                    st.plotly_chart(fig_blog, use_container_width=True)
                    
                    # 블로그 리스트 (Table 5)
                    st.write("### 수집된 블로그 게시물 요약 통계")
                    blog_summary = df_all_blog.groupby('keyword').size().reset_index(name='수집게시물수')
                    st.table(blog_summary)
                    
                    st.write("### 최신 블로그 헤드라인")
                    st.dataframe(df_all_blog[['keyword', 'title', 'postdate', 'link']].sort_values('postdate', ascending=False))
            
            with tab4:
                st.subheader("데이터 분석 원본 및 내보내기")
                col_down1, col_down2 = st.columns(2)
                with col_down1:
                    st.write("검색 트렌드 데이터 (2025)")
                    st.dataframe(df_trend)
                    st.download_button("Trend CSV 다운로드", df_trend.to_csv(index=False, encoding='utf-8-sig'), "trend_data.csv")
                
                with col_down2:
                    st.write("쇼핑 검색 데이터")
                    st.dataframe(df_all_shop)
                    st.download_button("Shopping CSV 다운로드", df_all_shop.to_csv(index=False, encoding='utf-8-sig'), "shopping_data.csv")
else:
    st.info("사이드바에서 키워드를 입력하고 '데이터 분석 실행' 버튼을 눌러주세요.")
