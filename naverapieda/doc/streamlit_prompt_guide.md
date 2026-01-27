# Naver API 기반 Streamlit 대시보드 제작 및 배포 가이드

이 문서는 범용적인 네이버 API 활용 대시보드 생성을 위한 LLM 프롬프트와 Streamlit Cloud 배포 시 보안 관리 방안을 설명합니다.

---

## 1. Streamlit 대시보드 생성용 범용 프롬프트 (LLM 전달용)

다음 프롬프트를 ChatGPT, Claude 등의 LLM에 입력하여 코드를 생성할 수 있습니다.

```text
[역할]
너는 파이썬과 Streamlit, Plotly 전문가야. 네이버 OpenAPI를 연동하여 사용자가 입력한 키워드에 대해 실시간 데이터를 수집하고 시각화하는 대시보드를 작성해줘.

[주요 기능]
1. 사이드바 구성:
   - 키워드 입력창 (쉼표로 구분하여 여러 개 입력 가능)
   - 조회 기간 설정 (시작일, 종료일)
   - 검색/분석 실행 버튼
2. 데이터 연동 (Naver API):
   - 검색어 트렌드 API (Datalab)
   - 쇼핑 검색 API
   - 블로그 검색 API
3. 대시보드 레이아웃 (Tabs 구성):
   - '트렌드 분석': Plotly 시계열 차트 및 요일별 히트맵
   - '쇼핑 분석': 가격 분포 히스토그램, 브랜드/판매처별 통계 그래프
   - '콘텐츠/Raw Data': 블로그 리스트 및 분석 원본 데이터 표 (CSV 다운로드 포함)
4. 보안 설정:
   - os.getenv()를 사용하여 NAVER_CLIENT_ID, NAVER_CLIENT_SECRET을 가져오도록 구현해줘.

[기술 요구사항]
- Visualization: Plotly Express 적극 활용
- UX: st.spinner를 사용하여 로딩 상태 표시, 데이터 부재 시 예외 처리
- 디자인: 깔끔하고 모던한 UI를 위해 st.set_page_config와 커스텀 CSS(간단히) 사용
```

---

## 2. Streamlit Cloud 배포 및 보안 관리 (Secrets)

로컬의 `.env` 파일은 보안상 GitHub에 올리면 안 됩니다. 대신 Streamlit Cloud의 **Secrets** 기능을 사용하여 관리합니다.

### 2.1 코드 수정 (범용성 확보)
코드 내에서 API 키를 불러올 때 아래와 같이 작성하면, 로컬(.env)과 서버(Secrets) 환경을 모두 지원합니다.

```python
import streamlit as st
import os
from dotenv import load_dotenv

# 로컬 실행 시 .env 로드 (서버에서는 환경변수가 직접 로드됨)
load_dotenv()

# 우선 순위: Streamlit Secrets > os.environ
CLIENT_ID = st.secrets.get("NAVER_CLIENT_ID") or os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = st.secrets.get("NAVER_CLIENT_SECRET") or os.getenv("NAVER_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    st.error("Naver API 자격 증명이 설정되지 않았습니다. .env 또는 Streamlit Secrets를 확인하세요.")
```

### 2.2 Streamlit Cloud Secrets 설정 방법
1. **GitHub Repository**: 로컬 프로젝트를 GitHub에 Push합니다. (이때 `.env`는 `.gitignore`에 반드시 포함)
2. **Deploy to Streamlit**: [Streamlit Cloud](https://share.streamlit.io/)에 접속하여 앱을 배포합니다.
3. **Advanced Settings**: 배포 창이나 대시보드의 `Settings` -> `Secrets` 메뉴로 들어갑니다.
4. **Secrets 입력**: 아래 형식을 복사해서 그대로 붙여넣습니다.

```toml
NAVER_CLIENT_ID = "여기에_클라이언트_ID를_넣으세요"
NAVER_CLIENT_SECRET = "여기에_클라이언트_시크릿을_넣으세요"
```

### 2.3 주의사항
- **.gitignore**: `.env` 파일이 GitHub에 올라가지 않도록 설정되어 있는지 재차 확인하십시오.
- **API 한도**: 배포된 앱을 여러 사람이 사용할 경우 네이버 API 일일 호출 한도(1,000회)에 도달할 수 있으므로 주의가 필요합니다.
