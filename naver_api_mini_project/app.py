import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 페이지 설정
st.set_page_config(page_title="K-디저트 트렌드 분석기", layout="wide")

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

def get_headers():
    return {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "Content-Type": "application/json"
    }

@st.cache_data(ttl=3600)  # 1시간 동안 캐시 유지
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

@st.cache_data(ttl=3600)
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

@st.cache_data(ttl=3600)
def fetch_shopping_search(keyword):
    url = f"https://openapi.naver.com/v1/search/shop.json?query={keyword}&display=50"
    res = requests.get(url, headers=get_headers())
    if res.status_code == 200:
        return res.json().get('items', [])
    return []

@st.cache_data(ttl=3600)
def fetch_blog_search(keyword):
    url = f"https://openapi.naver.com/v1/search/blog.json?query={keyword}&display=50"
    res = requests.get(url, headers=get_headers())
    if res.status_code == 200:
        return res.json().get('items', [])
    return []

# --- 사이드바 ---
st.sidebar.title("🏪 분석 설정")
category_name = st.sidebar.selectbox("카테고리 선택", list(CATEGORIES.keys()))
category_id = CATEGORIES[category_name]
keywords_input = st.sidebar.text_input("분석 키워드 (쉼표로 구분)", "두바이 초콜릿, 두쫀쿠로")
keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]

today = datetime.now()
date_range = st.sidebar.date_input("조회 기간", [today - timedelta(days=30), today])

# 분석 실행 버튼
run_analysis = st.sidebar.button("데이터 분석 실행")

# --- 메인 화면 ---
st.title("🍩 K-디저트 트렌드 실시간 분석 대시보드")
st.markdown("---")

if run_analysis:
    if not CLIENT_ID or not CLIENT_SECRET:
        st.error(".env 파일에 NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET을 설정해주세요.")
    else:
        with st.spinner("네이버 API에서 실시간 데이터를 수집 중입니다..."):
            all_trends = []
            all_shopping = []
            all_blogs = []
            
            for kw in keywords:
                # 1. 쇼핑 트렌드 수집 (부족 시 일반 검색 트렌드로 보충)
                st.write(f"🔍 '{kw}' 트렌드 수집 중...")
                trend = fetch_shopping_insight(kw, category_id, date_range[0], date_range[1])
                trend_type = "쇼핑 클릭" if trend else "일반 검색"
                
                if not trend:
                    trend = fetch_search_trend(kw, date_range[0], date_range[1])
                
                if trend:
                    for t in trend:
                        t['keyword'] = kw
                        t['type'] = trend_type
                    all_trends.extend(trend)
                
                # 2. 쇼핑 상품 수집
                products = fetch_shopping_search(kw)
                for p in products:
                    p['search_keyword'] = kw
                all_shopping.extend(products)
                
                # 3. 블로그 포스트 수집
                posts = fetch_blog_search(kw)
                for p in posts:
                    p['search_keyword'] = kw
                all_blogs.extend(posts)

            # DataFrame 변환
            df_trend = pd.DataFrame(all_trends)
            df_shop = pd.DataFrame(all_shopping)
            df_blog = pd.DataFrame(all_blogs)

            # 탭 구성
            tab1, tab2, tab3, tab4 = st.tabs(["📈 트랜드 분석", "🛒 쇼핑 데이터 분석", "📝 콘텐츠 EDA", "🗂️ 원본 데이터"])
            
            with tab1:
                if not df_trend.empty:
                    df_trend['period'] = pd.to_datetime(df_trend['period'])
                    st.subheader("키워드별 트렌드 비교")
                    # 데이터 출처 표시 (멀티 키워드일 수 있으므로 유니크한 타입들 추출)
                    types = df_trend['type'].unique()
                    st.caption(f"💡 데이터 제공 API: {', '.join(types)} 트렌드")
                    
                    fig1 = px.line(df_trend, x='period', y='ratio', color='keyword', 
                                  title="최근 30일 키워드별 트렌드 지수 변화",
                                  labels={'period': '날짜', 'ratio': '지수 (상대값)'})
                    st.plotly_chart(fig1, use_container_width=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("요약 통계표")
                        summary_table = df_trend.groupby('keyword')['ratio'].agg(['mean', 'max', 'min']).reset_index()
                        summary_table.columns = ['키워드', '평균 지수', '최대 지수', '최소 지수']
                        st.table(summary_table)
                    
                    with col2:
                        st.subheader("점유율 분석")
                        pie_data = df_trend.groupby('keyword')['ratio'].sum().reset_index()
                        fig2 = px.pie(pie_data, values='ratio', names='keyword', title="전체 트렌드 중 키워드별 비중")
                        st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.warning("분석 가능한 트렌드 데이터(쇼핑/검색)가 없습니다. 아주 새로운 키워드이거나 검색량이 매우 적을 수 있습니다.")

            with tab2:
                st.subheader("네이버 쇼핑 상품 분석")
                if not df_shop.empty:
                    # 전처리
                    df_shop['lprice'] = pd.to_numeric(df_shop['lprice'])
                    
                    col3, col4 = st.columns(2)
                    with col3:
                        st.subheader("키워드별 상품 가격 분포")
                        fig3 = px.box(df_shop, x='search_keyword', y='lprice', color='search_keyword',
                                     title="상품 최저가 분포 비교",
                                     labels={'search_keyword': '키워드', 'lprice': '최저가 (원)'})
                        st.plotly_chart(fig3, use_container_width=True)
                    
                    with col4:
                        st.subheader("주요 쇼핑몰 비중")
                        mall_counts = df_shop.groupby('mallName').size().nlargest(10).reset_index(name='count')
                        fig4 = px.bar(mall_counts, x='mallName', y='count', title="상위 10개 입점 쇼핑몰 분포")
                        st.plotly_chart(fig4, use_container_width=True)
                    
                    st.subheader("쇼핑몰별 평균 가격 대조")
                    mall_price = df_shop.groupby('mallName')['lprice'].mean().nlargest(10).reset_index()
                    st.dataframe(mall_price, use_container_width=True)
                else:
                    st.warning("쇼핑 상품 데이터가 없습니다.")

            with tab3:
                st.subheader("블로그 콘텐츠 분석")
                if not df_blog.empty:
                    col5, col6 = st.columns(2)
                    with col5:
                        st.subheader("블로거 분포 (출처별)")
                        blog_stats = df_blog.groupby('search_keyword').size().reset_index(name='게시글수')
                        fig5 = px.bar(blog_stats, x='search_keyword', y='게시글수', color='search_keyword',
                                     title="키워드별 블로그 검색 결과 수")
                        st.plotly_chart(fig5, use_container_width=True)
                    
                    with col6:
                        st.subheader("최신 블로그 포스트 리스트")
                        blog_list = df_blog[['search_keyword', 'title', 'postdate']].head(10)
                        blog_list['title'] = blog_list['title'].str.replace('<b>', '').str.replace('</b>', '')
                        st.table(blog_list)
                    
                    st.subheader("날짜별 블로그 작성 빈도 (Scatter)")
                    df_blog['postdate'] = pd.to_datetime(df_blog['postdate'])
                    blog_date_counts = df_blog.groupby(['postdate', 'search_keyword']).size().reset_index(name='count')
                    fig6 = px.scatter(blog_date_counts, x='postdate', y='count', color='search_keyword',
                                     size='count', title="블로그 포스트 작성 타임라인")
                    st.plotly_chart(fig6, use_container_width=True)
                else:
                    st.warning("블로그 데이터가 없습니다.")

            with tab4:
                st.subheader("수집된 원본 데이터 상세")
                col_raw1, col_raw2 = st.columns(2)
                with col_raw1:
                    st.write("📊 트렌드 원본")
                    st.dataframe(df_trend)
                with col_raw2:
                    st.write("🛒 쇼핑 상품 원본")
                    st.dataframe(df_shop)
else:
    st.info("사이드바에서 설정을 완료한 후 '데이터 분석 실행' 버튼을 눌러주세요.")
