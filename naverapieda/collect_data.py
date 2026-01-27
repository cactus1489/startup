import os
import json
import requests
import csv
from datetime import datetime
from dotenv import load_dotenv

# .env 파일 로드
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    print(f"Warning: .env file not found at {env_path}")

CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

def get_headers():
    return {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "Content-Type": "application/json"
    }

def save_to_csv(filename, data, fieldnames):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"Saved: {filename}")
    except Exception as e:
        print(f"Error saving {filename}: {e}")

def collect_shopping_trend(keywords_dict, start_date="2025-01-01", end_date="2025-12-31"):
    """
    쇼핑인사이트 키워드별 트렌드 수집 및 검색어 트렌드(Search) 백업 수집
    """
    # 1. 쇼핑인사이트 키워드 API (특정 분야 내 키워드 클릭 추이)
    url_shop = "https://openapi.naver.com/v1/datalab/shopping/category/keywords"
    # 2. 통합검색 트렌드 API (네이버 전체 검색 추이)
    url_search = "https://openapi.naver.com/v1/datalab/search"
    
    for name, keyword_list in keywords_dict.items():
        # 쇼핑 트렌드 시도
        body_shop = {
            "startDate": start_date,
            "endDate": end_date,
            "timeUnit": "date",
            "category": "50000007", # 식품 카테고리 ID로 수정
            "keyword": [{"name": name, "param": keyword_list}]
        }
        
        print(f"--- Processing: {name} ---")
        response = requests.post(url_shop, headers=get_headers(), data=json.dumps(body_shop))
        if response.status_code == 200:
            res_data = response.json()
            rows = res_data['results'][0]['data'] if 'results' in res_data and len(res_data['results']) > 0 else []
            print(f"[Shopping] Collected {len(rows)} data points.")
            
            if len(rows) > 0:
                today = datetime.now().strftime("%Y%m%d")
                filename = f"data/2025_{name}_shopping_trend_{today}.csv"
                save_to_csv(filename, rows, ["period", "ratio"])
                continue # 성공하면 다음 키워드로
            else:
                print(f"[Shopping] Data is empty for {name}. Falling back to General Search Trend...")
        else:
            print(f"Error {response.status_code} for {name} (Shopping): {response.text}")

        # 쇼핑 데이터가 부족하거나 실패 시 일반 통합검색 트렌드 시도
        body_search = {
            "startDate": start_date,
            "endDate": end_date,
            "timeUnit": "date",
            "keywordGroups": [{"groupName": name, "keywords": keyword_list}]
        }
        
        response = requests.post(url_search, headers=get_headers(), data=json.dumps(body_search))
        if response.status_code == 200:
            res_data = response.json()
            rows = res_data['results'][0]['data'] if 'results' in res_data else []
            print(f"[Search] Collected {len(rows)} data points.")
            
            if rows:
                today = datetime.now().strftime("%Y%m%d")
                filename = f"data/2025_{name}_general_search_trend_{today}.csv"
                save_to_csv(filename, rows, ["period", "ratio"])
        else:
            print(f"Error {response.status_code} for {name} (Search): {response.text}")

def collect_blog_search(keyword, display=10):
    url = f"https://openapi.naver.com/v1/search/blog.json?query={keyword}&display={display}"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        items = response.json().get('items', [])
        if items:
            today = datetime.now().strftime("%Y%m%d")
            filename = f"data/2025_{keyword}_blog_search_{today}.csv"
            keys = items[0].keys()
            save_to_csv(filename, items, keys)
    else:
        print(f"Error {response.status_code} for {keyword}: {response.text}")

def collect_shopping_search(keyword, display=10):
    url = f"https://openapi.naver.com/v1/search/shop.json?query={keyword}&display={display}"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        items = response.json().get('items', [])
        if items:
            today = datetime.now().strftime("%Y%m%d")
            filename = f"data/2025_{keyword}_shopping_search_{today}.csv"
            keys = items[0].keys()
            save_to_csv(filename, items, keys)
    else:
        print(f"Error {response.status_code} for {keyword}: {response.text}")

if __name__ == "__main__":
    if not CLIENT_ID or not CLIENT_SECRET or CLIENT_ID == "your_id_here":
        print("Error: API Client ID and Secret are not correctly set in .env file.")
    else:
        # 키워드 그룹 설정 (식품 카테고리 내 건강기능식품 위주로 5개 추가)
        keywords = {
            "오메가3": ["오메가3"],
            "비타민d": ["비타민d"],
            "유산균": ["유산균"],
            "루테인": ["루테인"],
            "밀크씨슬": ["밀크씨슬"],
            "콜라겐": ["콜라겐"],
            "마그네슘": ["마그네슘"]
        }
        
        collect_shopping_trend(keywords)
        for key in keywords.keys():
            collect_blog_search(key)
            collect_shopping_search(key)
