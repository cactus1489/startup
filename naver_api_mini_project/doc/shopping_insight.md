# 쇼핑인사이트 API 레퍼런스

## 1. 개요
쇼핑인사이트 API는 네이버 통합검색의 쇼핑 영역과 네이버쇼핑에서의 검색 클릭 추이 데이터를 JSON 형식으로 반환하는 RESTful API입니다.

- **호출 한도**: 하루 1,000회
- **인증 방식**: 비로그인 방식 (Client ID/Secret 사용)

## 2. API 상세

### 2.1 분야별 트렌드 조회
- **URL**: `https://openapi.naver.com/v1/datalab/shopping/categories`
- **Method**: `POST`
- **주요 파라미터**:
  - `startDate`: 조회 시작 날짜 (yyyy-mm-dd)
  - `endDate`: 조회 종료 날짜 (yyyy-mm-dd)
  - `timeUnit`: 구간 단위 (date, week, month)
  - `category`: 분야 설정 (name, param)

### 2.2 키워드별 트렌드 조회
- **URL**: `https://openapi.naver.com/v1/datalab/shopping/category/keywords`
- **Method**: `POST`
- **주요 파라미터**:
  - `category`: 쇼핑 분야 ID
  - `keyword`: 조회할 키워드 (name, param)

## 3. 구현 예제 (Python)
```python
#-*- coding: utf-8 -*-
import os
import sys
import urllib.request
import json

client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
url = "https://openapi.naver.com/v1/datalab/shopping/categories"
body = {
    "startDate": "2023-08-01",
    "endDate": "2023-09-30",
    "timeUnit": "month",
    "category": [{"name": "패션의류", "param": ["50000000"]}],
    "device": "pc",
    "ages": ["20", "30"],
    "gender": "f"
}

request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id",client_id)
request.add_header("X-Naver-Client-Secret",client_secret)
request.add_header("Content-Type","application/json")
response = urllib.request.urlopen(request, data=json.dumps(body).encode("utf-8"))
# ... 이후 응답 처리
```
