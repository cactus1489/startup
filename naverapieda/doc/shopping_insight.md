# 쇼핑인사이트 API 개발가이드

## 개요
쇼핑인사이트 API는 네이버 통합검색의 쇼핑 영역과 네이버쇼핑에서의 검색 클릭 추이 데이터를 JSON 형식으로 반환하는 RESTful API입니다.
- **방식**: 비로그인 방식 (Client ID/Secret 인증)
- **한도**: 하루 1,000회 호출 가능

## API 상세 (분야별 트렌드 조회)
- **URL**: `https://openapi.naver.com/v1/datalab/shopping/categories`
- **HTTP Method**: `POST`
- **헤더 필수값**:
    - `X-Naver-Client-Id`: 발급받은 클라이언트 아이디
    - `X-Naver-Client-Secret`: 발급받은 클라이언트 시크릿
    - `Content-Type`: `application/json`

## 주요 파라미터 (JSON)
| 파라미터 | 타입 | 설명 |
| :--- | :--- | :--- |
| `startDate` | string | 조회 시작 날짜 (YYYY-MM-DD) |
| `endDate` | string | 조회 종료 날짜 (YYYY-MM-DD) |
| `timeUnit` | string | 구간 단위 (date, week, month) |
| `category` | array | 카테고리 설정 (name, param(`cat_id`)) |
| `device` | string | 기기 범위 (pc, mo) |
| `gender` | string | 성별 범위 (m, f) |
| `ages` | array | 연령대 (10, 20, 30, 40, 50, 60) |

## 요청 예시 (Curl)
```bash
curl https://openapi.naver.com/v1/datalab/shopping/categories \
  --header "X-Naver-Client-Id: YOUR_CLIENT_ID" \
  --header "X-Naver-Client-Secret: YOUR_CLIENT_SECRET" \
  --header "Content-Type: application/json" \
  -d '{
    "startDate": "2023-01-01",
    "endDate": "2023-01-31",
    "timeUnit": "month",
    "category": [{"name": "패션의류", "param": ["50000000"]}],
    "device": "pc",
    "gender": "f",
    "ages": ["20", "30"]
  }'
```

## 응답 예시
응답 성공 시 `results` 객체 내에 `data` 배열을 포함하며, 각 데이터 포인트는 `period`와 `ratio`(최댓값 100 기준 상대값)를 가집니다.
