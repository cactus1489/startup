# 2025년 쇼핑 트렌드 데이터 수집 및 확인 작업지시서

이 문서는 네이버 쇼핑인사이트 API를 활용하여 2025년 한 해 동안의 일자별 쇼핑 클릭 트렌드 데이터를 수집하고 검증하는 절차를 정의합니다.

## 1. 작업 개요
- **목적**: 2025년 소비자 쇼핑 트렌드 변화 분석을 위한 데이터 확보
- **대상**: 네이버 쇼핑 특정 카테고리 (예: 패션의류)
- **수집 기간**: 2025-01-01 ~ 2025-12-31 (1년간)
- **수집 단위**: 일자별 (`date`)

## 2. 프로젝트 구조 (File Tree)
`naverapieda` 폴더 하위의 추천 구조입니다.
```text
naverapieda/
├── doc/
│   ├── datalab.md
│   ├── openapi_guide.md
│   ├── shopping_insight.md
│   ├── shopping_search.md
│   ├── README.md
│   └── shopping_trend_task.md (본 문서)
├── data/
│   └── 2025_fashion_clothing_daily_trend_20260107.csv (수집 결과물)
├── .env                       
# API 인증 정보 (Client ID, Secret)
├── .gitignore                 
# .env 등 민감 정보 제외 설정
├── shopping_trend_task.md     
# 현재 작업지시서
└── collect_data.py            
# 데이터 수집 실행 코드 (작성 예정)
```

## 3. 사전 준비 및 보안 사항
- **환경 변수 관리**: `client_id`와 `client_secret`은 루트나 폴더별 별도 프로젝트 환경이 아닌 `naverapieda/.env` 파일을 생성하여 관리합니다.
  - `.env` 파일 내용 예시:
    ```text
    NAVER_CLIENT_ID=your_id_here
    NAVER_CLIENT_SECRET=your_secret_here
    ```
- **환경 분리**: 루트 디렉토리의 `.venv` 가상환경을 활성화하여 사용합니다.

## 3. 수집 프로세스 및 상세 설정

### 3.1 요청 파라미터 구성
[shopping_insight.md](doc/shopping_insight.md) 가이드에 따라 다음과 같이 파라미터를 설정합니다.

| 항목 | 설정값 | 비고 |
| :--- | :--- | :--- |
| **URL** | `https://openapi.naver.com/v1/datalab/shopping/categories` | POST 방식 |
| **startDate** | `2025-01-01` | 수집 시작일 |
| **endDate** | `2025-12-31` | 수집 종료일 |
| **timeUnit** | `date` | 일자별 데이터 수집 |
| **category** | `{"name": "패션의류", "param": ["50000000"]}` | 분석 대상 카테고리 ID |
| **device/gender** | 필요 시 `pc`, `mo` / `m`, `f` 설정 | 기본값은 전체 |

### 3.2 수집 계획 (Logic Only)
1. **환경 변수 로드**: `.env` 파일에서 `NAVER_CLIENT_ID` 및 `NAVER_CLIENT_SECRET`을 읽어옵니다.
2. **API 요청 구성**: [shopping_insight.md](doc/shopping_insight.md) 가이드의 POST 사양에 맞춰 2025년 전체 기간을 일 단위로 요청합니다.
3. **데이터 파싱**: 응답받은 JSON에서 날짜(`period`)와 클릭 지수(`ratio`) 데이터를 추출합니다.
4. **CSV 저장**: 추출된 데이터를 지정된 규칙에 따라 CSV 파일로 명착하여 저장합니다.

## 4. 데이터 저장 및 확인

### 4.1 CSV 저장 규칙
데이터의 명확성을 위해 다음과 같은 명명 규칙을 준수합니다.
- **파일명 형식**: `[연도]_[카테고리명]_[수집단위]_trend_[수집실행날짜].csv`
- **파일명 예시**: `2025_fashion_clothing_daily_trend_20260107.csv`
- **필수 포함 내용**: 수집 대상 연도, 카테고리, 수집 날짜(YYYYMMDD)

### 4.2 데이터 검증 (Verification)
1. **누락 확인**: 데이터 포인트가 2025년 총 일수(365일)와 일치하는지 확인합니다.
2. **구조 확인**: CSV의 컬럼명이 `period`, `ratio`로 올바르게 구성되었는지 확인합니다.
3. **상대값 이해**: [datalab.md](doc/datalab.md)에 기술된 바와 같이, 기간 내 최대 클릭일을 100으로 설정한 상대값임을 인지하고 분석합니다.

## 5. 주의 사항
- **호출 제한**: 하루 호출 한도는 1,000회입니다. 반복 테스트 시 주의하십시오.
- **데이터 활용**: 수집된 데이터는 네이버 이용약관에 따라 분석 목적으로만 활용해야 합니다.
