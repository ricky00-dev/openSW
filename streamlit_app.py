import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import plotly.express as px
import pydeck as pdk
import requests
import streamlit as st


# -------------------------------------------------------------------
# 페이지 설정
# -------------------------------------------------------------------
st.set_page_config(page_title="날씨 대시보드", layout="wide")


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def get_api_key() -> Optional[str]:
    """Return OpenWeather API key from secrets if present."""
    try:
        return st.secrets["api_keys"]["openweather"]
    except (KeyError, FileNotFoundError):
        return None


def deg_to_direction(deg: float) -> str:
    """Convert wind degree to compass direction."""
    dirs = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]
    idx = int((deg / 22.5) + 0.5) % 16
    return dirs[idx]


def format_ts(ts: int, tz_offset: int) -> str:
    """Format unix timestamp with timezone offset seconds."""
    return (
        datetime.utcfromtimestamp(ts + tz_offset)
        .replace(tzinfo=timezone.utc)
        .strftime("%Y-%m-%d %H:%M")
    )


def geocode_city(city: str) -> Optional[Tuple[float, float]]:
    """Geocode city via Open-Meteo (no key required)."""
    if not city:
        return None
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        res = requests.get(url, params={"name": city, "count": 1}, timeout=10)
        if res.status_code != 200:
            return None
        data = res.json()
        if not data.get("results"):
            return None
        lat = data["results"][0]["latitude"]
        lon = data["results"][0]["longitude"]
        return float(lat), float(lon)
    except Exception:
        return None


# -------------------------------------------------------------------
# Data fetchers (cached)
# -------------------------------------------------------------------
@st.cache_data(ttl=600, show_spinner=False)
def fetch_current_openweather(
    api_key: str, city: Optional[str], units: str, lat: Optional[float], lon: Optional[float]
) -> Optional[Dict[str, Any]]:
    """Fetch current weather via OpenWeather."""
    try:
        base = "https://api.openweathermap.org/data/2.5/weather"
        params: Dict[str, Any] = {"appid": api_key, "units": units}
        if lat is not None and lon is not None:
            params.update({"lat": lat, "lon": lon})
        else:
            params["q"] = city
        res = requests.get(base, params=params, timeout=10)
        if res.status_code != 200:
            return None
        return res.json()
    except Exception:
        return None


@st.cache_data(ttl=600, show_spinner=False)
def fetch_forecast_openweather(
    api_key: str, city: Optional[str], units: str, lat: Optional[float], lon: Optional[float]
) -> Optional[Dict[str, Any]]:
    """Fetch 5-day / 3-hour forecast via OpenWeather."""
    try:
        base = "https://api.openweathermap.org/data/2.5/forecast"
        params: Dict[str, Any] = {"appid": api_key, "units": units}
        if lat is not None and lon is not None:
            params.update({"lat": lat, "lon": lon})
        else:
            params["q"] = city
        res = requests.get(base, params=params, timeout=10)
        if res.status_code != 200:
            return None
        return res.json()
    except Exception:
        return None


@st.cache_data(ttl=600, show_spinner=False)
def fetch_air_quality_openweather(api_key: str, lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Fetch air quality (AQI, PM, gases) via OpenWeather."""
    try:
        base = "https://api.openweathermap.org/data/2.5/air_pollution"
        params = {"appid": api_key, "lat": lat, "lon": lon}
        res = requests.get(base, params=params, timeout=10)
        if res.status_code != 200:
            return None
        return res.json()
    except Exception:
        return None


@st.cache_data(ttl=600, show_spinner=False)
def fetch_fallback_open_meteo(city: str, units: str) -> Optional[Dict[str, Any]]:
    """Fallback current + hourly forecast via Open-Meteo (no key)."""
    coords = geocode_city(city)
    if not coords:
        return None
    lat, lon = coords
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability",
            "current_weather": "true",
            "forecast_days": 5,
        }
        res = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=10)
        if res.status_code != 200:
            return None
        data = res.json()
        return {"raw": data, "lat": lat, "lon": lon, "units": units}
    except Exception:
        return None


@st.cache_data(ttl=600, show_spinner=False)
def detect_location_by_ip() -> Optional[Dict[str, Any]]:
    """Detect approximate location via IP."""
    try:
        res = requests.get("https://ipinfo.io/json", timeout=10)
        if res.status_code != 200:
            return None
        data = res.json()
        if "loc" not in data:
            return None
        lat_str, lon_str = data["loc"].split(",")
        return {
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country"),
            "lat": float(lat_str),
            "lon": float(lon_str),
        }
    except Exception:
        return None


# -------------------------------------------------------------------
# Sidebar
# -------------------------------------------------------------------
st.sidebar.title("날씨 설정")

default_cities = [
    "Seoul",
    "Busan",
    "Tokyo",
    "New York",
    "London",
    "Paris",
    "Sydney",
    "Beijing",
    "Los Angeles",
    "Singapore",
]

if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["Seoul"]

selected_city = st.sidebar.selectbox("도시 선택", default_cities, index=0)
custom_city = st.sidebar.text_input("다른 도시 검색", selected_city)
city = custom_city.strip() or selected_city

st.sidebar.markdown("---")
st.sidebar.subheader("즐겨찾기")

favorites = st.session_state["favorites"]
if st.sidebar.button("현재 도시를 즐겨찾기에 추가"):
    if city and city not in favorites:
        favorites.append(city)
        st.sidebar.success(f"'{city}'을(를) 즐겨찾기에 추가했어요.")
    else:
        st.sidebar.info("이미 즐겨찾기에 있거나 도시 이름이 비어 있어요.")

if favorites:
    fav_selected = st.sidebar.selectbox("즐겨찾기에서 선택", favorites, key="fav_select")
    if st.sidebar.button("선택한 즐겨찾기로 전환"):
        city = fav_selected
        st.sidebar.success(f"{fav_selected}(으)로 전환했습니다.")
else:
    st.sidebar.caption("즐겨찾기가 없습니다.")

st.sidebar.markdown("---")
unit_choice = st.sidebar.radio("단위 선택", ["섭씨 (°C)", "화씨 (°F)"])
units = "metric" if "섭씨" in unit_choice else "imperial"
unit_symbol = "°C" if units == "metric" else "°F"
wind_speed_unit = "m/s" if units == "metric" else "mph"

refresh = st.sidebar.button("새로고침 (캐시 초기화)")
if refresh:
    st.cache_data.clear()
    st.experimental_rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("위치")
use_my_location = st.sidebar.button("내 위치 사용 (IP 기반)")
location_override: Optional[Dict[str, Any]] = None
if use_my_location:
    location_override = detect_location_by_ip()
    if location_override:
        city = location_override.get("city") or city
        st.sidebar.success(
            f"감지됨: {location_override.get('city')}, {location_override.get('region')} ({location_override.get('country')})"
        )
    else:
        st.sidebar.error("위치를 감지할 수 없습니다.")

st.sidebar.markdown("---")
st.sidebar.subheader("알림")
rain_threshold = st.sidebar.slider("강수확률 경고 기준 (%)", 0, 100, 80, step=5)
hot_threshold = st.sidebar.slider(
    f"기온 경고 기준 (이상, {unit_symbol})",
    -20,
    45 if units == "metric" else 115,
    30 if units == "metric" else 86,
)

st.sidebar.markdown("---")
st.sidebar.subheader("경로 (선택)")
show_route = st.sidebar.checkbox("지도에 경로 표시")
route_from = st.sidebar.text_input("출발지 위도,경도", "")
route_to = st.sidebar.text_input("도착지 위도,경도", "")


# -------------------------------------------------------------------
# Data retrieval
# -------------------------------------------------------------------
api_key = get_api_key()
lat_override = location_override["lat"] if location_override else None
lon_override = location_override["lon"] if location_override else None

current_data: Optional[Dict[str, Any]] = None
forecast_data: Optional[Dict[str, Any]] = None
aq_data: Optional[Dict[str, Any]] = None
data_source = "OpenWeather"
fallback_data: Optional[Dict[str, Any]] = None

if api_key:
    current_data = fetch_current_openweather(api_key, city, units, lat_override, lon_override)
    forecast_data = fetch_forecast_openweather(api_key, city, units, lat_override, lon_override)
    if current_data and "coord" in current_data:
        aq_data = fetch_air_quality_openweather(api_key, current_data["coord"]["lat"], current_data["coord"]["lon"])
else:
    st.sidebar.warning("OpenWeather API 키가 없습니다. Open-Meteo 대체 모드로 동작합니다.")

if not current_data or not forecast_data:
    fallback_data = fetch_fallback_open_meteo(city, units)
    if fallback_data:
        data_source = "Open-Meteo (대체)"


# -------------------------------------------------------------------
# Safety checks and messaging
# -------------------------------------------------------------------
st.header("현재 날씨 대시보드")
if not (current_data or fallback_data):
    st.error("데이터를 불러올 수 없습니다. 도시 이름 또는 API 키(.streamlit/secrets.toml)를 확인해주세요.")
    st.stop()


# -------------------------------------------------------------------
# Prepare normalized frames
# -------------------------------------------------------------------
def build_forecast_df_from_openweather(raw: Dict[str, Any]) -> pd.DataFrame:
    rows = []
    tz_offset = raw.get("city", {}).get("timezone", 0)
    for item in raw.get("list", []):
        ts = item["dt"]
        rows.append(
            {
                "time": format_ts(ts, tz_offset),
                "temp": item["main"]["temp"],
                "feels_like": item["main"]["feels_like"],
                "humidity": item["main"]["humidity"],
                "pop": item.get("pop", 0) * 100,
                "weather": item["weather"][0]["description"],
            }
        )
    return pd.DataFrame(rows)


def build_forecast_df_from_open_meteo(raw: Dict[str, Any], units_local: str) -> pd.DataFrame:
    hourly = raw["raw"]["hourly"]
    times = hourly["time"]
    temps = hourly["temperature_2m"]
    hums = hourly["relative_humidity_2m"]
    pops = hourly.get("precipitation_probability", [0] * len(times))
    rows = []
    for t, temp, hum, pop in zip(times, temps, hums, pops):
        rows.append(
            {
                "time": t.replace("T", " "),
                "temp": temp if units_local == "metric" else temp * 9 / 5 + 32,
                "feels_like": temp if units_local == "metric" else temp * 9 / 5 + 32,
                "humidity": hum,
                "pop": pop,
                "weather": "",
            }
        )
    return pd.DataFrame(rows)


if current_data:
    city_name = current_data["name"]
    tz_offset = current_data.get("timezone", 0)
    lat = current_data["coord"]["lat"]
    lon = current_data["coord"]["lon"]
    updated_at = format_ts(current_data["dt"], tz_offset)
    current_temp = current_data["main"]["temp"]
    current_humidity = current_data["main"]["humidity"]
    current_aqi = aq_data["list"][0]["main"]["aqi"] if aq_data and aq_data.get("list") else None
else:
    city_name = city
    lat = fallback_data["lat"]
    lon = fallback_data["lon"]
    tz_offset = 0
    updated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    raw_current = fallback_data["raw"].get("current_weather", {})
    current_temp = raw_current.get("temperature")
    current_humidity = None
    current_aqi = None

if forecast_data:
    forecast_df = build_forecast_df_from_openweather(forecast_data)
else:
    forecast_df = build_forecast_df_from_open_meteo(fallback_data, units)


# -------------------------------------------------------------------
# KPI cards
# -------------------------------------------------------------------
card1, card2, card3, card4 = st.columns(4)
with card1:
    st.metric("도시 / 현지 시각", f"{city_name}", delta=updated_at)
with card2:
    st.metric("기온", f"{current_temp}{unit_symbol}")
with card3:
    st.metric("습도", f"{current_humidity if current_humidity is not None else '-'}%")
with card4:
    st.metric("AQI", current_aqi if current_aqi is not None else "N/A")

st.caption(f"데이터 출처: {data_source} • 갱신 시각: {updated_at}")


# -------------------------------------------------------------------
# Alerts
# -------------------------------------------------------------------
alert_msgs: List[str] = []
if not forecast_df.empty:
    max_pop = forecast_df["pop"].max()
    if max_pop >= rain_threshold:
        alert_msgs.append(f"높은 강수확률 예보가 있습니다 (최대 {max_pop:.0f}%).")
    max_temp = forecast_df["temp"].max()
    if max_temp >= hot_threshold:
        alert_msgs.append(f"높은 기온이 예상됩니다 (최대 {max_temp:.1f}{unit_symbol}).")

for msg in alert_msgs:
    st.warning(msg)


# -------------------------------------------------------------------
# Tabs
# -------------------------------------------------------------------
tab_weather, tab_air, tab_map = st.tabs(["날씨", "대기질", "지도/경로"])


# Weather tab
with tab_weather:
    st.subheader("기온 / 체감온도 (향후 5일)")
    if not forecast_df.empty:
        fig_temp = px.line(
            forecast_df,
            x="time",
            y=["temp", "feels_like"],
            labels={"value": f"기온 ({unit_symbol})", "time": "시간", "variable": "구분"},
            markers=True,
        )
        fig_temp.update_layout(legend_title=None)
        st.plotly_chart(fig_temp, use_container_width=True)

    st.subheader("습도")
    if not forecast_df.empty:
        fig_hum = px.line(
            forecast_df,
            x="time",
            y="humidity",
            labels={"humidity": "습도 (%)", "time": "시간"},
            markers=True,
        )
        st.plotly_chart(fig_hum, use_container_width=True)

    st.subheader("강수확률")
    if not forecast_df.empty:
        fig_pop = px.bar(
            forecast_df,
            x="time",
            y="pop",
            labels={"pop": "강수확률 (%)", "time": "시간"},
        )
        st.plotly_chart(fig_pop, use_container_width=True)

    with st.expander("상세 예보 표"):
        st.dataframe(forecast_df, use_container_width=True, height=300)

    csv_forecast = forecast_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="예보 CSV 다운로드",
        data=csv_forecast,
        file_name=f"{city_name}_forecast.csv",
        mime="text/csv",
    )

    current_payload = json.dumps(current_data or fallback_data, ensure_ascii=False, indent=2)
    st.download_button(
        label="현재 원본 데이터(JSON) 다운로드",
        data=current_payload,
        file_name=f"{city_name}_current.json",
        mime="application/json",
    )


# Air quality tab
with tab_air:
    if aq_data and aq_data.get("list"):
        st.subheader("대기질")
        aq_item = aq_data["list"][0]
        main_aqi = aq_item["main"]["aqi"]
        comps = aq_item.get("components", {})
        st.metric("AQI (1=좋음, 5=매우 나쁨)", main_aqi)
        cols = st.columns(5)
        pollutants = ["pm2_5", "pm10", "no2", "o3", "so2"]
        labels = {"pm2_5": "PM2.5", "pm10": "PM10", "no2": "NO₂", "o3": "O₃", "so2": "SO₂"}
        for col, key in zip(cols, pollutants):
            with col:
                st.metric(labels[key], f"{comps.get(key, 'N/A')} µg/m³")
        st.caption("OpenWeather Air Pollution API 기반 대기질 정보.")
    else:
        st.info("대기질 데이터를 불러올 수 없습니다 (API 키 필요).")


# Map / route tab
with tab_map:
    st.subheader("위치 지도")
    layers: List[pdk.Layer] = []
    point_df = pd.DataFrame({"lat": [lat], "lon": [lon], "city": [city_name]})
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=point_df,
            get_position="[lon, lat]",
            get_color="[200, 30, 0, 160]",
            get_radius=1200,
        )
    )

    if show_route and route_from and route_to:
        try:
            start_lat, start_lon = [float(x.strip()) for x in route_from.split(",")]
            end_lat, end_lon = [float(x.strip()) for x in route_to.split(",")]
            route_df = pd.DataFrame({"lat": [start_lat, end_lat], "lon": [start_lon, end_lon]})
            layers.append(
                pdk.Layer(
                    "LineLayer",
                    data=route_df,
                    get_source_position="[lon, lat]",
                    get_target_position="[lon, lat]",
                    get_color="[66, 135, 245, 200]",
                    get_width=4,
                )
            )
            layers.append(
                pdk.Layer(
                    "ScatterplotLayer",
                    data=route_df,
                    get_position="[lon, lat]",
                    get_color="[66, 135, 245, 200]",
                    get_radius=1000,
                )
            )
        except Exception:
            st.warning("경로 좌표를 해석할 수 없습니다. '위도,경도' 형태로 입력해주세요.")

    view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=9, pitch=45)
    chart_key = f"map-{city_name}-{lat:.4f}-{lon:.4f}"
    st.pydeck_chart(
        pdk.Deck(layers=layers, initial_view_state=view_state, tooltip={"text": "{city}"}),
        key=chart_key,
    )

    st.caption("경로 레이어는 단순 시각화용이며 실제 경로 탐색 엔진은 아닙니다.")


# -------------------------------------------------------------------
# Footer info
# -------------------------------------------------------------------
st.markdown("---")
st.caption(
    "`.streamlit/secrets.toml`에 API 키를 설정하세요:\n"
    "[api_keys]\nopenweather = \"YOUR_OPENWEATHER_KEY\"\nMAPBOX_API_KEY = \"YOUR_MAPBOX_KEY\""
)
