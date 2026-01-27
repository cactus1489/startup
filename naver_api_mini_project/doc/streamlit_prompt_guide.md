# Streamlit 대시보드 프롬프트 및 배포 가이드

이 문서는 AI를 활용하여 범용적인 네이버 API 대시보드를 생성하는 방법과 Streamlit Cloud 배포 시 보안 관리 방안을 설명합니다.

## 1. 범용 대시보드 생성을 위한 AI 프롬프트
다음 프롬프트를 복사하여 AI(ChatGPT, Claude 등)에게 전달하면 유사한 구조의 대시보드 코드를 얻을 수 있습니다.

> [!TIP]
> **프롬프트 내용:**
> "네이버 오픈 API(쇼핑인사이트, 검색)를 활용하여 실시간으로 키워드를 분석하는 범용 Streamlit 대시보드 파이썬 코드를 작성해줘.
> 1. 사용자가 사이드바에서 분석할 카테고리와 키워드(쉼표 구분)를 입력하고 '분석 실행' 버튼을 누르면 작동해야 함.
> 2. 시각화는 Plotly를 사용하고, 최소 5가지 이상의 차트(Line, Pie, Bar, Box, Scatter 등)를 포함해줘.
> 3. 분석 결과는 4개의 탭(트렌드, 쇼핑, 콘텐츠, Raw Data)으로 나누어 보여주고, 각 탭마다 요약 테이블을 포함해서 총 5개 이상의 표를 구현해줘.
> 4. 보안을 위해 API Client ID와 Secret은 환경 변수에서 로드하도록 구현해줘(로컬 .env 및 Streamlit Secrets 호환).
> 5. 성능 최적화를 위해 @st.cache_data를 적용한 API 호출 함수를 작성하고, 데이터가 없을 경우에 대한 예외 처리를 철저히 해줘."

---

## 2. 보안 관리 및 배포 가이드

### 2.1 로컬 환경 보안 설정 (.env)
로컬 개발 시에는 프로젝트 루트에 `.env` 파일을 생성하여 관리합니다.
1. **파일 생성**: `.env`
2. **내용 작성**:
   ```env
   NAVER_CLIENT_ID=여러분의_ID
   NAVER_CLIENT_SECRET=여러분의_Secret
   ```
3. **Python 코드 로드**:
   ```python
   from dotenv import load_dotenv
   import os
   load_dotenv()
   client_id = os.getenv("NAVER_CLIENT_ID")
   ```

### 2.2 Streamlit Cloud 배포 설정 (toml)
Streamlit Cloud에 배포할 때는 `.env` 파일을 올리지 않고, 서비스 내의 **Secrets** 기능을 사용합니다.

1. **로컬 테스트용 `.streamlit/secrets.toml` (옵션)**:
   배포 전 로컬에서 Secrets 기능을 테스트하려면 다음 위치에 파일을 만듭니다.
   - 위치: `naver_api_mini_project/.streamlit/secrets.toml`
   - 내용:
     ```toml
     NAVER_CLIENT_ID = "여러분의_ID"
     NAVER_CLIENT_SECRET = "여러분의_Secret"
     ```

2. **Streamlit Cloud 대시보드에서 설정**:
   - 배포된 앱의 [Settings] -> [Secrets] 메뉴로 이동합니다.
   - 아래와 같이 텍스트를 입력하고 저장합니다.
     ```toml
     NAVER_CLIENT_ID = "여러분의_ID"
     NAVER_CLIENT_SECRET = "여러분의_Secret"
     ```

3. **코드 내 Secrets 접근 방식**:
   Streamlit은 환경 변수와 Secrets를 자동으로 통합하므로 아래 코드로 둘 다 대응 가능합니다.
   ```python
   import streamlit as st
   import os

   # 1순위: st.secrets (배포 환경) / 2순위: os.getenv (로컬 .env)
   client_id = st.secrets.get("NAVER_CLIENT_ID") or os.getenv("NAVER_CLIENT_ID")
   client_secret = st.secrets.get("NAVER_CLIENT_SECRET") or os.getenv("NAVER_CLIENT_SECRET")
   ```

### 2.3 .gitignore 설정 (필수)
보안 정보가 GitHub에 유출되지 않도록 반드시 설정해야 합니다.
```bash
# .gitignore 내용
.env
.streamlit/secrets.toml
data/*.csv
```

---

## 3. 요약: 가상환경과 실제 서버의 차이
- **로컬**: `.env` 파일 + `python-dotenv` 라이브러리 활용.
- **배포**: Streamlit Cloud의 **Secrets 관리 도구** 활용 (코드는 수정 없이 자동 연동).
