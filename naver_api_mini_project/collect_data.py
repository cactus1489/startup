import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# .env 로드
load_dotenv()
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

def get_headers():
    return {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "Content-Type": "application/json"
    }

def save_to_csv(data, api_name, content_name):
    """
    수집한 데이터를 지정된 형식에 맞춰 CSV로 저장합니다.
    파일명 형식: {API}_{Content}_{Date}.csv
    """
    if not data:
        print(f"⚠️ {api_name} - {content_name}: 저장할 데이터가 없습니다.")
        return

    os.makedirs("data", exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    file_path = f"data/{api_name}_{content_name}_{today}.csv"
    
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False, encoding="utf-8-sig")
    print(f"✅ 저장 완료: {file_path}")

def collect_shopping_trend(keyword, category_id="50000007"):
    """네이버 쇼핑인사이트 키워드 클릭 트렌드 수집"""
    url = "https://openapi.naver.com/v1/datalab/shopping/category/keywords"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30) # 최근 1개월
    
    body = {
        "startDate": start_date.strftime("%Y-%m-%d"),
        "endDate": end_date.strftime("%Y-%m-%d"),
        "timeUnit": "date",
        "category": category_id,
        "keyword": [{"name": keyword, "param": [keyword]}]
    }
    
    response = requests.post(url, headers=get_headers(), data=json.dumps(body))
    if response.status_code == 200:
        results = response.json().get('results', [])
        if results and results[0].get('data'):
            return results[0]['data']
    else:
        print(f"❌ 쇼핑 트렌드 API 오류: {response.status_code}")
    return []

def collect_blog_search(keyword):
    """네이버 블로그 검색 결과 수집"""
    url = f"https://openapi.naver.com/v1/search/blog.json?query={keyword}&display=50"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        print(f"❌ 블로그 검색 API 오류: {response.status_code}")
    return []

def collect_shop_search(keyword):
    """네이버 쇼핑 상품 검색 결과 수집"""
    url = f"https://openapi.naver.com/v1/search/shop.json?query={keyword}&display=50"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        print(f"❌ 쇼핑 검색 API 오류: {response.status_code}")
    return []

if __name__ == "__main__":
    keywords = ["두바이 초콜릿", "두쫀쿠로"]
    
    for kw in keywords:
        print(f"\n🚀 '{kw}' 데이터 수집 시작...")
        
        # 1. 쇼핑 트렌드
        trend_data = collect_shopping_trend(kw)
        save_to_csv(trend_data, "shopping_trend", kw)
        
        # 2. 블로그 검색
        blog_data = collect_blog_search(kw)
        save_to_csv(blog_data, "blog_search", kw)
        
        # 3. 네이버 쇼핑 검색
        shop_data = collect_shop_search(kw)
        save_to_csv(shop_data, "shop_search", kw)

    print("\n✨ 모든 데이터 수집 작업 완료!")
