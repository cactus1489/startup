# Product Level 분석 테이블 생성 및 EDA

## 목표 산출물

- product_level_table.csv
- 상품 분석 시각화 이미지

---

## 1. 기준 정의

- 분석 단위: product_id
- 기준 테이블: transaction_level_table

---

## 2. 집계 수행

다음 기준으로 상품 단위 집계를 수행한다.

- 총 판매 수량
- 총 매출
- 평균 판매 단가
- 구매 household 수

---

## 3. 파생변수 생성

다음 파생변수를 생성한다.

- is_high_revenue_product (총 매출 상위 20%)
- is_frequent_product (구매 빈도 상위 20%)

---

## 4. 결과 저장

- 저장 경로: `./output/data/`
- 파일명: `product_level_table.csv`

---

## 5. EDA 및 시각화

다음 항목을 시각화한다.

- 상품 매출 상위 분포
- 카테고리별 매출 기여도
- 상품 판매량 분포
- 기타 인사이트를 발굴할 수 있는 기술통계 및 지표 분석
- 시각화 결과는 이미지로 저장
- 시각화 결과에 대한 해설과 EDA 보고서를 md파일로 저장

이미지 저장 규칙:

- 저장 경로: `./output/images/product/`
