# 쇼핑 검색 API 개발가이드

## 개요
네이버 검색의 쇼핑 검색 결과를 JSON 또는 XML 형식으로 반환하는 API입니다.
- **방식**: 비로그인 방식 (Client ID/Secret 인증)
- **HTTP Method**: `GET`

## API 상세 (쇼핑 검색 결과 조회)
- **URL (JSON)**: `https://openapi.naver.com/v1/search/shop.json`
- **URL (XML)**: `https://openapi.naver.com/v1/search/shop.xml`

## 주요 파라미터 (Query String)
| 파라미터 | 타입 | 필수 | 설명 |
| :--- | :--- | :--- | :--- |
| `query` | string | Y | 검색어 (UTF-8 인코딩 필수) |
| `display` | integer | N | 한 번에 표시할 검색 결과 개수 (기본 10, 최대 100) |
| `start` | integer | N | 검색 시작 위치 (기본 1, 최대 1000) |
| `sort` | string | N | 정렬 옵션 (sim: 유사도순(기기), date: 날짜순, asc: 가격 오름차순, dsc: 가격 내림차순) |
| `filter` | string | N | 필터링 옵션 (naverpay: 네이버페이 상품만) |
| `exclude` | string | N | 제외 옵션 (used: 중고, rental: 렌탈, cbshop: 해외직구) |

## 요청 예시 (Curl)
```bash
curl "https://openapi.naver.com/v1/search/shop.json?query=%EC%A3%BC%EC%8B%9D&display=10&start=1&sort=sim" \
  -H "X-Naver-Client-Id: YOUR_CLIENT_ID" \
  -H "X-Naver-Client-Secret: YOUR_CLIENT_SECRET"
```

## 응답 필드 (JSON 기준)
- `lastBuildDate`: 검색 결과 생성 시간
- `total`: 총 검색 결과 개수
- `start`: 검색 시작 위치
- `display`: 한 번에 표시된 결과 개수
- `items`: 개별 검색 결과 아이템 배열
    - `title`, `link`, `image`, `lprice`, `hprice`, `mallName`, `productId`, `productType`, `brand`, `category1~4` 등
    - `productType`: 1(일반상품), 2(중고상품), 3(단종상품), 4(판매예정상품)
