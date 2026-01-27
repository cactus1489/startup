# Customer Level 분석 테이블 생성

## 목표 산출물

- customer_level_table.csv
- 고객 분포 시각화 이미지

---

## 1. 기준 정의

- 분석 단위: household_key

---

## 2. 집계 수행

transaction_level_table을 활용하여
고객 단위 집계 테이블을 생성한다.

포함 컬럼:
- household_key
- total_transactions
- total_revenue
- avg_basket_value
- first_purchase_day
- last_purchase_day

---

## 3. 파생변수 생성

다음 파생변수를 생성한다.

- recency
- customer_lifetime_days

---

## 4. 결과 저장

- 저장 경로: `./output/data/`
- 파일명: `customer_level_table.csv`

---

## 5. EDA 및 시각화

다음 항목을 시각화한다.

- 고객 거래 횟수 분포
- 고객 총 매출 분포
- 고가치 고객 비중
- 기타 인사이트를 발굴할 수 있는 기술통계 및 지표 분석
- 시각화 결과는 이미지로 저장
- 시각화 결과에 대한 해설과 EDA 보고서를 md파일로 저장

이미지 저장 규칙:

- 저장 경로: `./output/images/customer/`
