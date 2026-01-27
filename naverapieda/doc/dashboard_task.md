# 네이버 데이터 분석 대시보드 구축 작업지시서

이 문서는 수집된 네이버 API 데이터를 기반으로 Streamlit과 Plotly를 활용하여 데이터 시각화 대시보드를 구축하기 위한 가이드를 제공합니다.

## 1. 프로젝트 목표
- **사용자 인터페이스**: Streamlit을 활용한 웹 기반 대시보드 구현
- **시각화 엔진**: Plotly를 활용한 인터랙티브 그래프 구현
- **핵심 기능**: 키워드 입력 기반 트렌드 수집 및 비교 분석
- **분석 범위**: 쇼핑 트렌드, 블로그 검색, 네이버쇼핑 검색 결과의 기초 EDA

## 2. 기술 스택 및 환경
- **Language**: Python 3.14+
- **Framework**: `streamlit`
- **Visualization**: `plotly`, `matplotlib` (보조)
- **Data Handling**: `pandas`, `json`, `csv`
- **Environment**: 프로젝트 루트의 `.venv` 가상환경 및 `.env` 파일(API Key) 활용

## 3. 대시보드 구조 및 레이아웃 (Tabs)
대시보드는 사이드바 메뉴와 메인 화면의 탭 구조로 구성합니다.

### 3.1 사이드바 (Sidebar)
- **API 인증 상태**: `.env` 파일 로드 확인
- **키워드 입력 필드**: 쉼표(,)로 구분된 다중 키워드 입력 가능하게 설정 (예: 오메가3, 비타민d)
- **수집 기간 설정**: 날짜 선택기(Date Picker)
- **실행 버튼**: 데이터 수집 및 업데이트 트리거

### 3.2 메인 화면 (Main Tabs)
1. **Trend Analysis**: 키워드별 검색 추이 비교
2. **Shopping EDA**: 가격, 몰(Mall) 정보 분석
3. **Content Insight**: 블로그 게시물 분석 (텍스트 기반)
4. **Raw Data**: 수집된 CSVRaw 데이터 확인

## 4. 시각화 상세 요구사항 (EDA)

### 4.1 그래프 구현 (5가지 이상)
1. **Multi-Line Chart**: 키워드별 시계열 검색 트렌드 비교 (Plotly Express)
2. **Trend Heatmap**: 요일별/월별 검색 강도 히트맵
3. **Bar Chart**: 쇼핑 검색 결과 내 상위 10개 판매처(Mall) 빈도 분석
4. **Histogram**: 검색된 상품의 가격 분포도 (Price Distribution)
5. **Scatter Plot**: 상품 가격 대비 리뷰 수(또는 브랜드별 분포) 상관관계 분석

### 4.2 표(Table) 구현 (5가지 이상)
1. **Summary Table**: 키워드별 연간 총 검색 지수 및 전월 대비 증감률
2. **Top 10 Products**: 네이버쇼핑 최저가 상위 10개 리스트
3. **Blog Content List**: 수집된 블로그 제목 및 요약 내용 요약 테이블
4. **Price Stats Table**: 카테고리별/키워드별 평균가, 중간값, 최대/최소값 통계
5. **Trend Peak Table**: 기간 내 검색량이 급증했던 특정 날짜 및 사유(키워드) 추출표

## 5. 단계별 구현 계획 (Logic)
1. **Data Loader (src/loader.py)**: `collect_data.py`의 수집 로직을 Streamlit 내부에서 호출하거나 기존 CSV를 로드하는 모듈 작성
2. **Layout Setup (app.py)**: `st.set_page_config`, `st.sidebar`, `st.tabs` 기본 골격 구성
3. **Visualization Module (src/viz.py)**: Plotly를 활용한 공통 그래프 생성 함수 구현
4. **EDA Logic**: 수집된 CSV 데이터를 Pandas DataFrame으로 변환 후 통계 처리 및 데이터 정제
5. **Interactive Filter**: 슬라이더나 셀렉트박스를 통해 특정 기간이나 가격대 필터링 기능 추가

## 6. 주의 사항
- **반응성**: 데이터 수집 시 API 호출 지연을 고려하여 `st.spinner` 활용
- **인코딩**: 한글 깨짐 방지를 위해 그래프 폰트 설정 및 CSV 읽기 시 `utf-8-sig` 적용
- **데이터 보안**: `.env` 파일이 외부에 노출되지 않도록 주의
