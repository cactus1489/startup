# Transaction Level EDA 보고서

## 1. 분석 개요
본 보고서는 `transaction_data`와 `product` 테이블을 결합하여 가구 및 장바구니 단위의 소비 패턴을 분석한 결과입니다.

- **분석 데이터**: `transaction_level_table.csv`
- **주요 파생변수**: `week`, `month`, `is_weekend`

## 2. 데이터 결합 결과
- `transaction_data`와 `product`를 `PRODUCT_ID` 기준으로 `Left Join` 하였습니다.
- 결합된 테이블을 통해 각 거래 건의 부서(`DEPARTMENT`) 및 상품 카테고리(`COMMODITY_DESC`) 정보를 확인할 수 있습니다.

## 3. 시각화 분석 결과

### 3-1. 일자별 거래 추이
![일자별 거래 추이](file:///C:/Users/dlstj/OneDrive/Desktop/ICB6/projec_join/output/images/product/daily_transaction_count.png)
- 시간이 지남에 따라 전체적인 거래 건수(Unique Basket ID)가 증가하는 추세를 보입니다.

### 3-2. 월별 매출 동향
![월별 매출 추이](file:///C:/Users/dlstj/OneDrive/Desktop/ICB6/projec_join/output/images/product/monthly_sales_trend.png)
- 30일 단위로 구축한 월별 매출액 비교 시, 후반부로 갈수록 매출 규모가 확장되는 양상을 보입니다.

### 3-3. 평일 vs 주말 매출 비중
![평일 주말 매출 비중](file:///C:/Users/dlstj/OneDrive/Desktop/ICB6/projec_join/output/images/product/weekend_sales_ratio.png)
- 전체 매출의 약 **28.4%**가 주말에 발생하며, 평일 대비 주말의 일평균 매출이 다소 높을 가능성을 시사합니다.

### 3-4. 주요 매출 발생 부서
![상위 부서 매출](file:///C:/Users/dlstj/OneDrive/Desktop/ICB6/projec_join/output/images/product/top_dept_sales.png)
- **GROCERY** 부서가 압도적인 매출 1위를 차지하고 있으며, **DRUG GM**, **PRODUCE**, **MEAT** 순으로 뒤를 잇고 있습니다.

## 4. 인사이트 요약
1. **성장 추세**: 데이터셋의 관측 기간 동안 거래량과 매출액이 우상향하고 있습니다.
2. **카테고리 집중**: 식료품(Grocery)과 잡화(Drug GM)가 전체 매출의 핵심 동력입니다.
3. **쇼핑 주기**: 특정 주차나 일자에 거래가 집중되는 패턴이 관찰되므로, 이를 캠페인 일정과 연계하여 분석할 필요가 있습니다.
