# Dunnhumby 데이터 ERD 작성 및 구조 이해

## 목표 산출물

- Dunnhumby ERD 이미지 파일

---

## 1. 대상 테이블

분석에 사용할 테이블은 projec_join/data 폴더에 위치한 테이블을 사용한다.

---

## 2. 테이블 구조 정리

각 테이블에 대해 다음을 정리한다.

- Primary Key
- Foreign Key
- 행(Row)이 의미하는 분석 단위

---

## 3. ERD 작성

다음 기준으로 ERD를 작성한다.

- household_key를 기준으로 관계 구조 정리
- product_id 기준 상품 연결 관계 명확히 표현
- transaction_data 중심의 1:N 관계 표현
- 캠페인/쿠폰 테이블은 연결 가능한 관계만 표현
- 작성된 ERD를 기반으로 보고서를 작성하고 md파일로 저장
---

## 4. ERD 저장

- 저장 경로: `./output/erd/`

---

## 5. 점검

- 어떤 테이블이 고객 단위 분석에 직접 사용 가능한가
- 어떤 테이블은 보조 정보에 해당하는가
