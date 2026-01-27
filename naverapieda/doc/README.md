# Naver API EDA Documentation

이 폴더는 네이버 API를 활용한 데이터 분석(EDA)을 위해 수집된 공식 문서들을 포함하고 있습니다.

## 문서 목록
1. [데이터랩 개요](datalab.md): 통합검색어 트렌드 및 쇼핑인사이트 서비스 소개
2. [쇼핑인사이트 개발가이드](shopping_insight.md): 쇼핑 카테고리/키워드별 클릭 트렌드 API 상세
3. [오픈API 공통 가이드](openapi_guide.md): 비로그인 방식 API 호출 및 인증 방법
4. [쇼핑 검색 개발가이드](shopping_search.md): 네이버 쇼핑 검색 결과 조회 API 상세
5. [2025 쇼핑트렌드 수집 지시서](../shopping_trend_task.md): 2025년 데이터 수집 구체적 절차 및 가이드
6. [데이터 분석 대시보드 지시서](dashboard_task.md): Streamlit & Plotly를 활용한 데이터 시각화 구축 가이드

## 활용 가이드
- 모든 API는 **비로그인 방식**으로, 발급받은 `Client ID`와 `Client Secret`을 헤더에 포함하여 호출합니다.
- 각 문서에는 주요 파라미터와 요청 예시(Curl)가 포함되어 있습니다.
