# 날씨 대시보드 (Streamlit)

신규 문서: [사용자 가이드](USER_GUIDE.md) · [개발자 가이드](DEVELOPER_GUIDE.md)

Streamlit 기반의 날씨·대기질 대시보드입니다.

## 주요 기능
- OpenWeather: 현재 날씨, 5일/3시간 예보, 대기질(AQI/미세먼지/가스).
- Open-Meteo 대체 경로: OpenWeather 키가 없을 때 제한적으로 날씨만 제공.
- 도시 검색·즐겨찾기, IP 기반 위치 감지, 섭씨/화씨 전환, 수동 새로고침.
- KPI 카드, 기온/체감온도·습도·강수확률 차트, 확장 가능한 예보 표.
- 강수확률·고온 알림, 예보 CSV 다운로드, 현재 데이터 JSON 다운로드.
- Pydeck 지도: 위치 마커 + 선택적 경로(단순 선 표시).

## 설정
1) 가상환경 생성 후 패키지 설치:
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # PowerShell
# source .venv/bin/activate    # macOS/Linux

pip install -r requirements.txt
```

2) `.streamlit/secrets.toml`에 키 추가:
```
[api_keys]
openweather = "YOUR_OPENWEATHER_KEY"   # 필수
MAPBOX_API_KEY = "YOUR_MAPBOX_KEY"     # 선택: 내 Mapbox 토큰/스타일을 쓸 때만 설정
```

3) 실행:
```
streamlit run streamlit_app.py
```

## 참고
- IP 기반 위치는 `ipinfo.io`를 사용합니다. 더 안정적인 사용을 원하면 해당 서비스의 개인 키를 설정하세요.
- 브라우저 위치 권한을 사용하려면 `streamlit-geolocation`이 설치되어 있어야 합니다(`requirements.txt`에 포함).
- 경로 오버레이는 두 좌표를 선으로 잇는 시각화만 제공하며, 실제 경로 탐색 엔진이 아닙니다.
- OpenWeather 키가 없으면 대기질은 표시되지 않고, Open-Meteo를 통해 날씨 정보만 제공합니다.

## 상세 사용 방법
1) 환경 준비
   - Python 3.9+ 권장
   - 가상환경 생성 후 `pip install -r requirements.txt`

2) API 키 설정
   - `.streamlit/secrets.toml` 생성 후 아래처럼 입력:
     ```
     [api_keys]
     openweather = "YOUR_OPENWEATHER_KEY"   # 필수
     MAPBOX_API_KEY = "YOUR_MAPBOX_KEY"     # 선택: 내 Mapbox 토큰/스타일을 쓸 때만 설정
     ```
   - OpenWeather 키가 없으면 대기질 패널이 비활성화되고, Open-Meteo로 날씨만 표시됩니다.

3) 실행
   - `streamlit run streamlit_app.py`
   - 사이드바에서 도시를 선택하거나 검색, 즐겨찾기 추가, 단위(섭씨/화씨) 변경, IP 기반 위치 사용 가능
   - "새로고침(캐시 초기화)" 버튼으로 캐시를 비우고 다시 요청할 수 있습니다.

4) 데이터 확인/다운로드
   - 예보 표는 익스팬더에서 확인하고 CSV로 다운로드 가능
   - 현재 응답 원본(JSON)도 다운로드 가능

5) 지도/경로
   - 기본 위치 마커 제공
   - "지도에 경로 표시" 체크 후 `출발지 위도,경도`, `도착지 위도,경도` 입력 시 두 점을 선으로 연결해 표시

6) 알림
   - 강수확률/고온 임계값을 사이드바에서 조정하면 상단에 경고가 표시됩니다.

## 파일 구조
- `streamlit_app.py` : 메인 앱 (app.py는 옛 버전, 사용하지 않음)
- `.streamlit/secrets.toml` : API 키 설정 (로컬 전용, 커밋 금지)
- `requirements.txt` : 의존성 목록
- `README.md` : 본 문서

## 대체 모드(Fallback)
- OpenWeather 호출 실패 또는 키 없음:
  - Open-Meteo 지오코딩 + 예보 사용
  - 대기질 패널 미표시, 일부 필드(체감온도/습도)만 제공
  - 데이터 출처에 "Open-Meteo (대체)"로 표시

## 자주 묻는 질문(FAQ) / 트러블슈팅
- API 키 없음/오류: 사이드바에 경고가 표시되며 대체 모드로 전환됩니다. 키를 올바르게 입력 후 새로고침하세요.
- 지도 스타일이 안 보임: Mapbox 키가 없으면 기본 스타일 사용. 키를 넣으면 Mapbox 스타일을 사용할 수 있습니다.
- 예보가 비어 있음: 도시명이 정확한지 확인하거나, 다른 도시로 테스트하세요. 호출 제한 시 잠시 후 재시도.
- 한글 깨짐: 터미널/OS 인코딩을 UTF-8로 맞추거나, Streamlit 실행 시 기본 인코딩을 확인하세요.

## 개발/테스트 메모
- 캐시는 `@st.cache_data`로 10분(ttl=600초) 유지됩니다.
- 네트워크/환경 문제로 API 실패 시 None을 반환하므로, 데이터 유효성 체크를 건드릴 때 이 부분을 고려하세요.
- 유닛 테스트는 포함되어 있지 않습니다. 배포 전 수동으로 주요 도시를 몇 개 선택해 동작을 확인하는 것을 권장합니다.
