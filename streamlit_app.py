import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import pydeck as pdk

# 페이지 설정
st.set_page_config(page_title="Weather Dashboard", layout="wide")

# 1 API 키 불러오기
# Streamlit 클라우드 배포 시 st.secrets에서 API 키를 설정해야 합니다.
# 로컬 테스트 시: API_KEY = "YOUR_OWN_API_KEY"
try:
    API_KEY = st.secrets["api_keys"]["openweather"]
except (FileNotFoundError, KeyError):
    # 로컬에서 st.secrets가 없을 경우를 대비한 대체 값 (실제 키로 변경 필요)
    st.warning("OpenWeather API 키를 st.secrets에서 찾을 수 없습니다. 'YOUR_OWN_API_KEY'를 사용합니다.")
    st.warning("배포 시에는 Streamlit Secrets에 API 키를 설정해야 합니다.")
    API_KEY = "YOUR_OWN_API_KEY" # 👈 로컬 테스트 시 본인의 API 키를 여기에 입력하세요

# 2 사이드바 설정
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
unit_symbol = "°C" if units == "metric" else "°F"

# 3 API 호출 함수
# 현재 날씨 API
@st.cache_data(ttl=600)
def fetch_weather(city_name, units):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units={units}"
    try:
        res = requests.get(url)
        res.raise_for_status() # HTTP 오류가 발생하면 예외 발생
        return res.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching current weather: {e}")
        return None

# 5일/3시간 예보 API (Plotly 차트용)
@st.cache_data(ttl=600)
def fetch_forecast(city_name, units):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={API_KEY}&units={units}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching forecast: {e}")
        return None

# 4 메인 화면 출력
st.header(f"🌍 Current Weather Dashboard")

if city:
    data_current = fetch_weather(city, units)
    data_forecast = fetch_forecast(city, units)

    # 두 API 호출이 모두 성공했는지 확인
    if data_current and data_forecast:
        st.subheader(f"📍 {data_current['name']}의 현재 날씨")

        # --- 현재 날씨 메트릭 ---
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("기온", f"{data_current['main']['temp']}{unit_symbol}")
            st.write(f"체감온도: {data_current['main']['feels_like']}{unit_symbol}")
        with col2:
            st.metric("습도", f"{data_current['main']['humidity']}%")
            st.write(f"기압: {data_current['main']['pressure']} hPa")
        with col3:
            st.metric("풍속", f"{data_current['wind']['speed']} m/s")
            st.write(f"날씨 상태: {data_current['weather'][0]['description']}")
        
        st.divider()

        # --- Plotly 시간별 기온 변화 그래프 ---
        st.subheader("🕰 3시간 간격 기온 예보 (Plotly)")

        try:
            # 예보 데이터 파싱
            forecast_list = data_forecast['list']
            
            # Pandas DataFrame 생성
            timestamps = [item['dt_txt'] for item in forecast_list]
            temperatures = [item['main']['temp'] for item in forecast_list]
            
            df_forecast = pd.DataFrame({
                'Time': pd.to_datetime(timestamps),
                'Temperature': temperatures
            })

            # Plotly 라인 차트 생성
            fig = px.line(
                df_forecast, 
                x='Time', 
                y='Temperature', 
                title=f"{data_current['name']}의 3시간 간격 기온 변화",
                markers=True
            )
            
            # 차트 레이아웃 업데이트
            fig.update_layout(
                xaxis_title="시간",
                yaxis_title=f"기온 ({unit_symbol})"
            )
            
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Plotly 차트를 생성하는 중 오류가 발생했습니다: {e}")

        st.divider()

        # --- Pydeck 도시 위치 지도 ---
        st.subheader("🗺 도시 위치 (Pydeck)")

        try:
            # 위도, 경도 추출
            lat = data_current['coord']['lat']
            lon = data_current['coord']['lon']
            
            map_data = pd.DataFrame({'lat': [lat], 'lon': [lon]})

            # Pydeck 뷰 상태 설정
            view_state = pdk.ViewState(
                latitude=lat,
                longitude=lon,
                zoom=10,
                pitch=50,
            )

            # Pydeck 레이어 설정 (ScatterplotLayer)
            layer = pdk.Layer(
                'ScatterplotLayer',
                data=map_data,
                get_position='[lon, lat]',
                get_color='[200, 30, 0, 160]', # RGBA 색상
                get_radius=1000, # 미터 단위
            )

            # Pydeck 맵 렌더링
            r = pdk.Deck(
                layers=[layer], 
                initial_view_state=view_state,
                map_style='mapbox://styles/mapbox/light-v9', # Mapbox 스타일
                tooltip={"text": f"{data_current['name']}\nLat: {lat}, Lon: {lon}"}
            )
            
            # Mapbox API 키가 필요할 수 있습니다. 
            # st.secrets에 "MAPBOX_API_KEY"가 있다면 자동으로 사용됩니다.
            st.pydeck_chart(r)
        
        except Exception as e:
            st.error(f"Pydeck 맵을 생성하는 중 오류가 발생했습니다: {e}")


    else:
        st.error("❌ API 호출 실패 - 도시 이름이나 API 키를 확인하세요.")
else:
    st.info("왼쪽에서 도시를 선택하거나 직접 입력해주세요 🌏")