import asyncio
import random
import os
import csv
import shutil
from datetime import datetime
from playwright.async_api import async_playwright

# scraper_base.md 지침에 따른 기본 설정
CONFIG = {
    "random_delay_min": 1,
    "random_delay_max": 3,
    "scroll_min_px": 500,
    "scroll_max_px": 1000,
    "items_per_page": 40,
    "max_pages": 4,
    "max_items": 40
}

class NaverShoppingScraper:
    def __init__(self, search_query):
        self.search_query = search_query
        self.base_url = "https://www.naver.com"
        self.search_url = f"https://search.shopping.naver.com/search/all?query={search_query}"
        self.results = []
        self.visited_ids = set()
        
        # 저장 폴더 구조 생성
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = os.path.join("crolling", "runs", f"run_{self.timestamp}")
        os.makedirs(self.run_dir, exist_ok=True)
        
    async def random_delay(self, factor=1.0):
        delay = random.uniform(CONFIG["random_delay_min"], CONFIG["random_delay_max"]) * factor
        await asyncio.sleep(delay)

    async def apply_stealth(self, page):
        """수동 스텔스 설정"""
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', {get: () => ['ko-KR', 'ko', 'en-US', 'en']});
        """)

    async def smooth_scroll(self, page):
        current_scroll = 0
        total_height = await page.evaluate("document.body.scrollHeight")
        while current_scroll < total_height:
            scroll_step = random.randint(CONFIG["scroll_min_px"], CONFIG["scroll_max_px"])
            current_scroll += scroll_step
            await page.evaluate(f"window.scrollTo(0, {current_scroll})")
            await asyncio.sleep(random.uniform(0.5, 1.0))
            total_height = await page.evaluate("document.body.scrollHeight")
            if current_scroll > total_height: break

    async def extract_items(self, page):
        # 최신 네이버 쇼핑 상품 목록 셀렉터
        item_selectors = [
            'div[class*="product_item__"]',
            'li[class*="product_item__"]',
            'div[class*="basicList_item__"]',
            'div[class*="adProduct_item__"]'
        ]
        
        items = []
        for selector in item_selectors:
            found = await page.query_selector_all(selector)
            if found:
                items.extend(found)
        
        if not items:
            items = await page.query_selector_all('div:has(a[class*="product_link"])')

        new_count = 0
        for item in items:
            if len(self.results) >= CONFIG["max_items"]:
                break
                
            try:
                title_el = await item.query_selector('a[class*="product_link"]')
                if not title_el: continue
                
                title = (await title_el.inner_text()).strip()
                detail_url = await title_el.get_attribute("href")
                
                item_id = detail_url if detail_url else title
                if not item_id or item_id in self.visited_ids:
                    continue
                
                brand_el = await item.query_selector('a[class*="product_mall"], span[class*="product_mall"]')
                brand = (await brand_el.inner_text()).strip() if brand_el else ""
                
                price_el = await item.query_selector('span[class*="price_num"]')
                price = (await price_el.inner_text()).strip() if price_el else "0"
                
                review_el = await item.query_selector('em[class*="product_num"], span[class*="product_num"]')
                review = (await review_el.inner_text()).strip() if review_el else "0"
                
                item_data = {
                    "item_id_or_url": item_id,
                    "brand": brand,
                    "title": title,
                    "korean_title": title,
                    "price": price,
                    "like": "0",
                    "review": review,
                    "detail_url": detail_url
                }
                
                self.results.append(item_data)
                self.visited_ids.add(item_id)
                new_count += 1
            except:
                continue
        
        print(f"📦 현재 페이지 신규 수집: {new_count}개 (총 {len(self.results)}개)")
        return new_count > 0

    async def run(self):
        async with async_playwright() as p:
            # Firefox 사용 시도
            browser = await p.firefox.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
                locale="ko-KR",
                timezone_id="Asia/Seoul"
            )
            
            page = await context.new_page()
            await self.apply_stealth(page)
            
            print(f"🚀 사이트 접속 시도: {self.base_url}")
            # domcontentloaded로 타임아웃 방지
            await page.goto(self.base_url, wait_until="domcontentloaded", timeout=60000)
            await self.random_delay(factor=1)
            
            print(f"🚀 검색 결과로 이동: {self.search_url}")
            await page.goto(self.search_url, wait_until="domcontentloaded", timeout=60000)
            
            # 페이지 확인
            content = await page.content()
            if "접속이 일시적으로 제한되었습니다" in content:
                print("❌ 차단 감지됨. 스크래핑을 중단합니다.")
                await browser.close()
                return

            current_page = 1
            while current_page <= CONFIG["max_pages"] and len(self.results) < CONFIG["max_items"]:
                print(f"📄 {current_page} 페이지 처리 중...")
                await page.wait_for_load_state("load", timeout=60000)
                await self.random_delay()
                await self.smooth_scroll(page)
                
                await self.extract_items(page)
                
                if len(self.results) >= CONFIG["max_items"]:
                    break
                
                next_btn = await page.query_selector('a[class*="pagination_next"]')
                if next_btn:
                    await next_btn.scroll_into_view_if_needed()
                    await self.random_delay()
                    await next_btn.click()
                    current_page += 1
                else:
                    break
            
            await browser.close()
            self.save_results()

    def save_results(self):
        if not self.results:
            print("⚠️ 수집된 데이터가 없어 파일을 저장하지 않습니다.")
            return

        csv_file = os.path.join(self.run_dir, f"result_{self.timestamp}.csv")
        fieldnames = ["item_id_or_url", "brand", "title", "korean_title", "price", "like", "review", "detail_url"]
        
        with open(csv_file, mode='w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)
            
        script_copy = os.path.join(self.run_dir, f"script_{self.timestamp}.py")
        shutil.copy(__file__, script_copy)
        
        print(f"✅ 최종 저장 완료 (총 {len(self.results)}개): {csv_file}")

if __name__ == "__main__":
    query = "두바이 초콜릿"
    scraper = NaverShoppingScraper(query)
    asyncio.run(scraper.run())
