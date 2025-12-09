# 개발자 가이드 - 날씨 대시보드

프로젝트 구조, 설정, 개발 워크플로를 정리했습니다.

## 환경 준비
- Python 3.9+ 권장.
- 가상환경 생성 후 의존성 설치:
  ```
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1    # PowerShell
  pip install -r requirements.txt
  ```
- 비밀값 설정: `.streamlit/secrets.toml`
  ```
  [api_keys]
  openweather = "YOUR_OPENWEATHER_KEY"
  MAPBOX_API_KEY = "YOUR_MAPBOX_KEY"
  ```

## 주요 파일
- `streamlit_app.py`: 앱 엔트리포인트. 사이드바 설정, 데이터 수집/정규화, 시각화, 다운로드 UI를 모두 포함합니다.
- `app.py`: 초기(또는 경량) 버전. 현재는 `streamlit_app.py` 사용을 권장합니다.
- `.streamlit/secrets.toml`: API 키 저장용(버전에 포함되지 않음).
- `requirements.txt`: 의존성 목록.

## 아키텍처 개요 (`streamlit_app.py`)
- **데이터 수집**: OpenWeather(현재/5일 예보/대기질) + 실패 시 Open-Meteo(현재/시간별 예보) 대체 경로.
- **보조 기능**: Open-Meteo 지오코딩으로 도시 → 좌표 변환, `ipinfo.io` 기반 IP 위치 감지, 선택적 `streamlit-geolocation`을 통한 브라우저 좌표 획득.
- **상태 관리**: `st.session_state`로 즐겨찾기 목록 유지.
- **캐싱**: `st.cache_data(ttl=600)`으로 API 호출 결과 캐시, 사이드바 버튼으로 즉시 초기화.
- **시각화**: Plotly(기온·체감온도·습도·강수확률), Pydeck(지도/경로 오버레이), Streamlit metric 카드.
- **다운로드**: 예보 CSV, 현재 원본 JSON 다운로드 버튼 제공.
- **알림**: 강수확률/고온 기준을 슬라이더로 받아 상단 경고 배너 출력.

## 개발/디버깅 워크플로
- 실행: `streamlit run streamlit_app.py`
- 캐시 초기화: 앱 사이드바 버튼 또는 CLI에서 `streamlit cache clear`.
- 브라우저 위치 테스트: `streamlit-geolocation`이 설치되어 있어야 하며, 권한 팝업을 허용해야 합니다.
- API 키 없이도 기본 흐름(Open-Meteo 대체 모드) 테스트가 가능하지만, 대기질/정확한 예보 확인은 OpenWeather 키가 필요합니다.

## 의존성 및 업데이트
- 새 패키지 추가 시 `requirements.txt`를 함께 업데이트합니다.
- Plotly/Pydeck/Streamlit 버전업 시 UI 동작 여부를 수동 확인합니다(자동 테스트 미제공).

## 품질 체크 포인트
- **네트워크 실패**: API 호출이 `None`을 반환할 수 있으므로 UI가 안전하게 메시지를 보여주는지 확인.
- **좌표 파싱**: 경로 입력(`위도,경도`)에서 float 캐스팅 오류가 나면 경고가 표시되는지 확인.
- **단위 변환**: 섭씨/화씨 선택 시 체감온도·강수확률·습도 그래프가 일관된지 확인.

## 배포 힌트
- Streamlit Cloud 또는 사내 인프라에 배포 시 `.streamlit/secrets.toml`의 API 키만 환경 변수나 시크릿으로 주입하면 됩니다.
- 캐시 TTL(600초)이나 레이아웃 설정은 `st.cache_data`와 `st.set_page_config`에서 바로 수정 가능합니다.

