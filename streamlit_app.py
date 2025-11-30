import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import pydeck as pdk
from datetime import datetime
def deg_to_direction(deg: float) -> str:
    """풍향(각도)을 16방위 문자열로 변환"""
    dirs = [
        "N", "NNE", "NE", "ENE",
        "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW",
        "W", "WNW", "NW", "NNW",
    ]
    idx = int((deg / 22.5) + 0.5) % 16
    return dirs[idx]


# -------------------------------------------------------------------
# 페이지 설정
# -------------------------------------------------------------------
st.set_page_config(page_title="Weather Dashboard", layout="wide")

# -------------------------------------------------------------------
# 1. API 키 불러오기 (Streamlit Secrets 사용)
# -------------------------------------------------------------------
API_KEY = ""
try:
    # st.secrets에서 OpenWeather 키를 읽어옵니다.
    API_KEY = st.secrets["api_keys"]["openweather"]
except (FileNotFoundError, KeyError):
    # 로컬에서 st.secrets가 없을 경우 경고
    st.error("🚨 OpenWeather API 키를 찾을 수 없습니다.")
    st.info("이 앱을 실행하려면 .streamlit/secrets.toml 파일에 OpenWeather API 키를 설정해야 합니다.")
    st.stop()  # API 키가 없으면 앱 실행 중지

# -------------------------------------------------------------------
# 2. 사이드바 설정
# -------------------------------------------------------------------
st.sidebar.title("🌤 Weather Settings")

# 기본 도시 목록
default_cities = [
    "Seoul", "Busan", "Tokyo", "New York", "London",
    "Paris", "Sydney", "Beijing", "Los Angeles", "Singapore"
]
# ⭐ Streamlit 세션에 즐겨찾기 리스트 저장
if "favorites" not in st.session_state:
    # 처음에는 기본으로 Seoul 하나 넣어두기 (원하면 빈 리스트로 해도 됨)
    st.session_state["favorites"] = ["Seoul"]

# 인기 도시 선택 (드롭다운)
selected_city = st.sidebar.selectbox("Select a City", default_cities, index=0)

# 직접 검색 입력 (기본값은 선택한 도시)
custom_city = st.sidebar.text_input("Or search another city", selected_city)

# 최종적으로 선택된 도시
city = custom_city

# ⭐ 즐겨찾기 영역
st.sidebar.markdown("---")
st.sidebar.subheader("⭐ 즐겨찾기")

favorites = st.session_state["favorites"]

# 1) 현재 도시 즐겨찾기에 추가
if st.sidebar.button("현재 도시 즐겨찾기에 추가"):
    if custom_city and custom_city not in favorites:
        favorites.append(custom_city)
        st.sidebar.success(f"'{custom_city}' 를 즐겨찾기에 추가했습니다.")
    elif custom_city in favorites:
        st.sidebar.info("이미 즐겨찾기에 있는 도시입니다.")

# 2) 즐겨찾기에서 선택해 바로 보기
if favorites:
    fav_selected = st.sidebar.selectbox(
        "즐겨찾기에서 도시 선택", favorites, key="favorite_select"
    )
    if st.sidebar.button("이 즐겨찾기 도시로 보기"):
        city = fav_selected
        st.sidebar.success(f"현재 도시를 '{fav_selected}'로 변경했습니다.")
else:
    st.sidebar.caption("아직 즐겨찾기 도시가 없습니다. 위 버튼으로 추가해 보세요.")

st.sidebar.markdown("---")

# 단위 선택
unit_choice = st.sidebar.radio("Select Unit", ["Celsius (°C)", "Fahrenheit (°F)"])
units = "metric" if "Celsius" in unit_choice else "imperial"
unit_symbol = "°C" if units == "metric" else "°F"
wind_speed_unit = "m/s" if units == "metric" else "mph"

# -------------------------------------------------------------------
# 3. API 호출 함수
# -------------------------------------------------------------------
@st.cache_data(ttl=600)
def fetch_weather(city_name, units):
    """현재 날씨 데이터를 API에서 가져옵니다."""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units={units}"
    res = requests.get(url)

    # ❶ 없는 도시
    if res.status_code == 404:
        return None

    # ❷ 그 외 API 실패
    if res.status_code != 200:
        return None

    # ❸ 정상일 때만
    return res.json()

@st.cache_data(ttl=600)
def fetch_forecast(city_name, units):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={API_KEY}&units={units}"
    res = requests.get(url)

    if res.status_code == 404:
        return None

    if res.status_code != 200:
        return None

    return res.json()


# -------------------------------------------------------------------
# 4. 메인 화면 출력
# -------------------------------------------------------------------
st.header("🌍 Current Weather Dashboard")

if city:
    data_current = fetch_weather(city, units)
    data_forecast = fetch_forecast(city, units)

     # ✅ 현재 날씨 데이터 못 가져온 경우 (없는 도시 포함)
    if not data_current:
        st.error(f"❌ '{city}' 는(은) 존재하지 않는 도시입니다. 도시 이름을 다시 확인해주세요.")
        st.stop()

    # ✅ 예보 데이터만 실패한 경우
    if not data_forecast:
        st.error("❌ 예보 데이터를 불러오는 데 실패했습니다. 잠시 후 다시 시도해주세요.")
        st.stop()

    # 여기까지 왔으면 둘 다 정상
    st.subheader(f"📍 {data_current['name']}의 현재 날씨")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        icon_url = f"https://openweathermap.org/img/wn/{data_current['weather'][0]['icon']}@2x.png"
        st.image(icon_url, width=80, caption=f"{data_current['weather'][0]['description']}")
    with col2:
        st.metric("기온", f"{data_current['main']['temp']}{unit_symbol}")
        st.write(f"체감온도: {data_current['main']['feels_like']}{unit_symbol}")
    with col3:
        st.metric("습도", f"{data_current['main']['humidity']}%")
        st.write(f"기압: {data_current['main']['pressure']} hPa")
    with col4:
    # 풍속
     wind_speed = data_current.get("wind", {}).get("speed", None)
    wind_deg = data_current.get("wind", {}).get("deg", None)
    visibility = data_current.get("visibility", None)  # m 단위
    clouds = data_current.get("clouds", {}).get("all", None)  # %

    if wind_speed is not None:
        st.write(f"풍속: {wind_speed:.1f} {wind_speed_unit}")
    if wind_deg is not None:
        st.write(f"풍향: {deg_to_direction(wind_deg)} ({wind_deg}°)")
    if visibility is not None:
        st.write(f"시정: {visibility/1000:.1f} km")
    if clouds is not None:
        st.write(f"구름량: {clouds}%")

    st.divider()

    st.subheader("🌡 3시간 간격 기온 예보 (Plotly)")
    try:
        forecast_data = [(item['dt_txt'], item['main']['temp']) for item in data_forecast['list']]
        df = pd.DataFrame(forecast_data, columns=['Time', 'Temperature'])
        df['Time'] = pd.to_datetime(df['Time'])
        fig = px.line(df, x='Time', y='Temperature',
                        title=f"{data_current['name']} 기온 변화",
                        labels={'Time': '시간', 'Temperature': f'기온 ({unit_symbol})'})
        fig.update_traces(mode='lines+markers', line_shape='spline')
        st.plotly_chart(fig, use_container_width=True)

        # --- CSV 다운로드 버튼 추가 ---
        csv = df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📥 3시간 예보 CSV 다운로드",
            data=csv,
            file_name=f"{data_current['name']}_forecast.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"차트 생성 중 오류 발생: {e}")

    st.divider()

    st.subheader("🗺 도시 위치 (Pydeck)")

    mapbox_key = None
    try:
        # [api_keys] "서랍 안"에서 Mapbox 키를 조용히 읽어옵니다.
        mapbox_key = st.secrets["api_keys"]["MAPBOX_API_KEY"]
    except (KeyError, FileNotFoundError):
        # 키가 없으면 mapbox_key는 None으로 유지됩니다.
        pass

    try:
        lat = data_current['coord']['lat']
        lon = data_current['coord']['lon']

        layer = pdk.Layer(
            'ScatterplotLayer',
            data=pd.DataFrame({'lat': [lat], 'lon': [lon]}),
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',  # RGBA (빨간색)
            get_radius=1000,
        )

        view_state = pdk.ViewState(
            latitude=lat,
            longitude=lon,
            zoom=10,
            pitch=50,
        )

        if mapbox_key:
            r = pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                map_style='mapbox://styles/mapbox/light-v9',
                api_keys={'mapbox': mapbox_key},
                tooltip={"text": f"{data_current['name']}\nLat: {lat}, Lon: {lon}"}
            )
            st.pydeck_chart(r)
        else:
            st.warning("🗺️ Mapbox API 키가 .streamlit/secrets.toml에 설정되지 않아 지도를 표시할 수 없습니다.")
    except Exception as e:
        st.error(f"Pydeck 맵 생성 중 오류 발생: {e}")
else:
    st.info("왼쪽 사이드바에서 도시를 선택하거나 직접 검색해주세요 🌏")
