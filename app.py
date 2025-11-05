import streamlit as st
import requests

# 페이지 설정
st.set_page_config(page_title="Weather Dashboard", layout="wide")

# 1️⃣ API 키 불러오기
API_KEY = st.secrets["api_keys"]["openweather"]

# 2️⃣ 사이드바 설정
st.sidebar.title("🌤 Weather Settings")

# 기본 도시 목록
default_cities = [
    "Seoul", "Busan", "Tokyo", "New York", "London",
    "Paris", "Sydney", "Beijing", "Los Angeles", "Singapore"
]

# 인기 도시 선택 (드롭다운)
selected_city = st.sidebar.selectbox("Select a City", default_cities, index=0)

# 직접 검색 입력 (기본값은 선택한 도시)
custom_city = st.sidebar.text_input("Or search another city", selected_city)

# 최종적으로 선택된 도시
city = custom_city

# 단위 선택
unit_choice = st.sidebar.radio("Select Unit", ["Celsius (°C)", "Fahrenheit (°F)"])
units = "metric" if "Celsius" in unit_choice else "imperial"

# 3️⃣ API 호출 함수
@st.cache_data(ttl=600)
def fetch_weather(city_name, units):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units={units}"
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()
    else:
        return None

# 4️⃣ 메인 화면 출력
st.header(f"🌍 Current Weather Dashboard")

if city:
    data = fetch_weather(city, units)

    if data:
        st.subheader(f"📍 {data['name']}의 현재 날씨")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("기온", f"{data['main']['temp']}°")
            st.write(f"체감온도: {data['main']['feels_like']}°")
        with col2:
            st.metric("습도", f"{data['main']['humidity']}%")
            st.write(f"기압: {data['main']['pressure']} hPa")
        with col3:
            st.metric("풍속", f"{data['wind']['speed']} m/s")
            st.write(f"날씨 상태: {data['weather'][0]['description']}")


    else:
        st.error("❌ API 호출 실패 - 도시 이름이나 API 키를 확인하세요.")
else:
    st.info("왼쪽에서 도시를 선택하거나 직접 입력해주세요 🌏")

