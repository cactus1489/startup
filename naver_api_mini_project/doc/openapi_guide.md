# 네이버 오픈 API 공통 가이드 (비로그인 방식)

## 1. 비로그인 방식 개요
비로그인 방식 오픈 API는 네이버 로그인의 인증을 통한 접근 토큰을 획득할 필요 없이, HTTP 헤더에 **클라이언트 아이디**와 **클라이언트 시크릿** 값만 전송해 사용할 수 있는 API입니다.

## 2. 주요 비로그인 API 리스트
- **데이터랩**: 검색어 트렌드, 쇼핑인사이트
- **검색**: 뉴스, 블로그, 쇼핑, 웹 사이트 등 분야별 검색 결과
- **이미지/음성 캡차**: 자동 가입 방지 기능
- **공유하기**: 블로그, 카페 등에 콘텐츠 공유
- **Clova Face Recognition**: 얼굴 인식 및 감지

## 3. 주요 요청 URL 정보

| API명 | 요청 URL | 메서드 |
| :--- | :--- | :--- |
| 통합검색어 트렌드 | `https://openapi.naver.com/v1/datalab/search` | POST |
| 쇼핑 분야별 트렌드 | `https://openapi.naver.com/v1/datalab/shopping/categories` | POST |
| 블로그 검색 | `https://openapi.naver.com/v1/search/blog` | GET |
| 쇼핑 검색 | `https://openapi.naver.com/v1/search/shop` | GET |
