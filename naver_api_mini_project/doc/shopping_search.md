# 쇼핑 검색 API 레퍼런스

## 1. 개요
쇼핑 검색 API는 네이버 검색의 쇼핑 검색 결과를 XML 또는 JSON 형식으로 반환하는 API입니다.

## 2. API 상세
- **URL**: `https://openapi.naver.com/v1/search/shop.json`
- **Method**: `GET`
- **인증**: 비로그인 방식 (HTTP 헤더에 Client ID/Secret 추가)

## 3. 주요 파라미터 (Query String)
- `query`: 검색어 (UTF-8 인코딩 필수)
- `display`: 한 번에 표시할 검색 결과 개수 (최대 100)
- `start`: 검색 시작 위치 (최대 1000)
- `sort`: 정렬 옵션 (`sim`: 유사도순, `date`: 날짜순, `asc`: 가격오름차순, `dsc`: 가격내림차순)

## 4. 응답 필드
- `title`: 상품명
- `link`: 상품 상세 URL
- `image`: 상품 이미지 URL
- `lprice`: 최저가 정보
- `hprice`: 최고가 정보
- `mallName`: 쇼핑몰 명칭
- `brand`: 브랜드 정보
- `category1~4`: 카테고리 분류 정보

## 5. 요청 예시 (Curl)
```bash
curl "https://openapi.naver.com/v1/search/shop.json?query=주식&display=10&start=1&sort=sim" \
  -H "X-Naver-Client-Id: {CLIENT_ID}" \
  -H "X-Naver-Client-Secret: {CLIENT_SECRET}" -v
```
