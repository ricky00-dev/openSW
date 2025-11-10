🌤 Streamlit 날씨 대시보드

이 프로젝트는 Streamlit과 OpenWeather API를 사용하여 실시간 날씨 정보를 보여주는 대시보드입니다.

🚀 로컬에서 실행하기

1. 저장소 복제 (Clone)

git clone (이 저장소의 URL)
cd (저장소 폴더 이름)


2. 가상 환경 생성 및 활성화

# 'venv'라는 이름의 가상 환경 폴더 생성
python -m venv venv

# Windows (CMD)
.\venv\Scripts\activate
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# macOS / Linux
source venv/bin/activate


3. 필수 라이브러리 설치

pip install -r requirements.txt


(참고: 아직 requirements.txt 파일이 없다면, pip install streamlit plotly pandas pydeck을 직접 실행하세요.)

4. (⭐ 중요) API 키 설정하기

이 앱을 실행하려면 OpenWeatherMap API 키가 필요합니다.

OpenWeatherMap에 가입하여 API 키를 발급받으세요. (무료 플랜의 'Current Weather and Forecasts' API)

이 프로젝트의 .streamlit 폴더 안에 있는 secrets.toml.example 파일을 복사합니다.

.streamlit 폴더 안에 secrets.toml이라는 이름으로 붙여넣기 합니다.

방금 만든 secrets.toml 파일을 열고, openweather = "YOUR_KEY_HERE" 부분을 본인의 실제 API 키로 교체합니다.

.streamlit/secrets.toml 파일 예시:

[api_keys]
openweather = "a1b2c3d4e5f67890...." # 본인의 실제 키


5. Streamlit 실행

streamlit run streamlit_app.py