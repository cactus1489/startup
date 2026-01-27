# Naver API Mini Project 설계 계획서

이 문서는 네이버 오픈 API를 활용한 데이터 수집 프로젝트의 구조와 운영 규칙을 정의합니다.

## 1. 프로젝트 파일 트리 구조
```text
naver_api_mini_project/
├── doc/                        # API 개발 가이드 및 문서 (수집 완료)
│   ├── datalab.md
│   ├── shopping_insight.md
│   ├── openapi_guide.md
│   └── shopping_search.md
├── data/                       # 수집된 데이터 저장소
│   ├── [내용]_[날짜].csv        # CSV 명명 규칙 적용
│   └── ...
├── .env                        # API 클라이언트 정보 (보안 관리)
├── .gitignore                  # 보안 및 불필요 파일 제외 설정
├── collect_data.py             # 데이터 수집 메인 스크립트 (기획 예정)
└── README.md                   # 프로젝트 개요 설명서
```

## 2. 데이터 저장 규칙 (CSV)
수집된 데이터는 `data/` 폴더 내에 저장하며, 파일명만 보고도 내용을 파악할 수 있도록 다음과 같은 형식을 따릅니다.

- **파일명 형식**: `{API종류}_{수집대상}_{수집날짜}.csv`
- **예시**:
  - `shopping_trend_food_20260110.csv` (식품 카테고리 쇼핑 트렌드)
  - `shopping_search_omega3_20260110.csv` (오메가3 쇼핑 검색 결과)
  - `blog_search_vitamin_20260110.csv` (비타민 블로그 검색 결과)
  - 'data/blog_search_두쫀쿠로_20260110.csv'
  - 'data/shop_search_두쫀쿠로_20260110.csv'

## 3. 보안 및 환경 변수 관리
API 인증 정보가 코드에 직접 노출되지 않도록 `.env` 파일을 통해 관리합니다.

- **.env 구성 내용**:
  ```text
  NAVER_CLIENT_ID=여러분의_클라이언트_ID
  NAVER_CLIENT_SECRET=여러분의_클라이언트_시크릿
  ```
- **주의사항**: 오픈 소스 저장소(GitHub 등)에 업로드할 때 `.env` 파일이 포함되지 않도록 `.gitignore`에 등록합니다.

## 4. 향후 작업 단계 (기획)
1. **환경 구축**: `.env` 파일 생성 및 필요한 라이브러리 선정.
2. **수집 기능 설계**: 각 API별 요청 함수 및 CSV 저장 유틸리티 기획.
3. **통합 실행 로직**: 설정된 키워드와 카테고리에 대해 일괄 수집하는 흐름 설계.
