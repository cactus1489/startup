# Transaction Level 분석 테이블 생성 및 EDA

## 목표 산출물

- transaction_level_table.csv
- Transaction Level 시각화 이미지

---

## 1. 기준 정의

- 분석 단위: basket_id
- 기준 테이블: transaction_data

---

## 2. JOIN 수행

다음 JOIN을 수행한다.

- transaction_data ⟵ product
- JOIN KEY:
  - transaction_data.product_id = product.product_id
- JOIN 방식: left join

---

## 3. 컬럼 구성

Transaction Level 테이블은 다음 컬럼을 포함한다.

- household_key
- basket_id
- day
- product_id
- department
- commodity_desc
- quantity
- sales_value

---

## 4. 날짜 파생변수 생성

기준 컬럼: day

생성 파생변수:
- week
- month
- is_weekend (임의 기준 정의 가능)

---

## 5. 결과 저장

- 저장 경로: `./output/data/`
- 파일명: `transaction_level_table.csv`

---

## 6. EDA 및 시각화

다음 항목을 분석한다.

- 일자별 거래 건수
- 월별 매출 추이
- 요일(또는 week 기준)별 매출 분포
- 기타 인사이트를 발굴할 수 있는 기술통계 및 지표 분석
- 시각화 결과는 이미지로 저장
- 시각화 결과에 대한 해설과 EDA 보고서를 md파일로 저장

이미지 저장 규칙:

- 저장 경로: `./output/images/product/`
