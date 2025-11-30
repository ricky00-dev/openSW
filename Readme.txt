🌤 Weather Dashboard (Streamlit)

OpenWeather API와 Mapbox를 사용해
현재 날씨 / 5일 예보 / 지도 시각화 / 즐겨찾기 기능을 제공하는
인터랙티브 Streamlit 대시보드입니다.

🚀 1. 로컬에서 실행하기
📌 1) 저장소 복제 (Clone)
git clone <이 저장소 URL>
cd openSW

📌 2) 가상환경 생성 및 활성화
python -m venv .venv

# PowerShell
.\.venv\Scripts\Activate.ps1

# CMD
.\.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

📌 3) 필수 라이브러리 설치
pip install -r requirements.txt


requirements.txt가 없다면:

pip install streamlit requests pandas plotly pydeck

📌 4) (⭐ 중요) API 키 설정하기

이 프로젝트는 2개의 API 키가 필요합니다.

1) OpenWeatherMap API 키

회원가입 → Current Weather & Forecast API 키 복사

https://openweathermap.org/api

2) Mapbox API 키

회원가입 또는 로그인 → Default Public Token 복사

https://account.mapbox.com

🔧 secrets.toml 설정 방법

.streamlit/secrets.toml.example 파일 복사

.streamlit/secrets.toml 으로 이름 변경

아래처럼 본인의 키 입력

[api_keys]
openweather = "YOUR_OPENWEATHER_KEY"
MAPBOX_API_KEY = "YOUR_MAPBOX_KEY"


⚠️ 이 파일은 절대 GitHub에 업로드되지 않습니다.

📌 5) 앱 실행
streamlit run streamlit_app.py

📊 기능 목록
✔ 현재 날씨 정보

기온

체감온도

습도

기압

풍속 / 풍향 / 시정 / 구름량 (추가됨)

날씨 아이콘 표시

✔ 5일 예보 (3시간 간격)

Plotly 기반 스무스 곡선 그래프

시간별 기온 변화 시각화

✔ 지도 시각화 (Pydeck + Mapbox)

선택한 도시의 위도/경도 표시

줌/피치 지원

마커 및 툴팁 표시

✔ 즐겨찾기 기능 (NEW)

사용자가 자주 조회하는 도시 저장

사이드바에서 빠르게 선택 가능

✔ 검색 기능

도시 검색

기본 제공 인기 도시 목록 (서울/부산/도쿄/뉴욕/런던…)

✔ 예외 처리

존재하지 않는 도시명 입력 시 오류 메시지 표시

API 호출 실패 시 사용자 경고

✔ 캐싱 기능

@st.cache_data로 API 호출 최적화

불필요한 요청 감소

📁 프로젝트 구조
openSW/
│
├── streamlit_app.py        # 최종 실행 파일 (app.py는 사용 X)
├── requirements.txt
├── README.md
└── .streamlit/
    ├── secrets.toml.example
    └── secrets.toml (로컬 전용)


⚠ app.py는 초기 버전으로 현재 사용하지 않습니다.
streamlit_app.py가 최종 메인 파일입니다.

🤝 협업 방식

팀원별 feature 브랜치 생성

Pull Request(PR)로 병합

main 브랜치만 배포/실행용으로 사용

secrets 파일은 각자 로컬에서만 관리

🎯 제출 안내

이 README와 streamlit_app.py, .streamlit/secrets.toml 설정 만으로
누구나 동일한 환경에서 앱을 실행할 수 있습니다.
