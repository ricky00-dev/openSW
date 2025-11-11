import streamlit as st
    import requests
    import pandas as pd
    import plotly.express as px
    import pydeck as pdk
    from datetime import datetime
    
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
        st.stop() # API 키가 없으면 앱 실행 중지
    
    # -------------------------------------------------------------------
    # 2. 사이드바 설정
    # -------------------------------------------------------------------
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
    wind_speed_unit = "m/s" if units == "metric" else "mph"
    
    # -------------------------------------------------------------------
    # 3. API 호출 함수
    # -------------------------------------------------------------------
    
    @st.cache_data(ttl=600)
    def fetch_weather(city_name, units):
        """현재 날씨 데이터를 API에서 가져옵니다."""
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units={units}"
        try:
            res = requests.get(url)
            res.raise_for_status() # 200 OK가 아니면 에러 발생
            return res.json()
        except requests.exceptions.HTTPError as err:
            st.error(f"❌ API 호출 실패 (도시: {city_name}): {err}")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"❌ 네트워크 연결 오류: {e}")
            return None
    
    @st.cache_data(ttl=600)
    def fetch_forecast(city_name, units):
        """5일간 3시간 간격 예보 데이터를 API에서 가져옵니다."""
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={API_KEY}&units={units}"
        try:
            res = requests.get(url)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.RequestException as e:
            st.error(f"❌ (Forecast) API 호출 실패: {e}")
            return None
    
    # -------------------------------------------------------------------
    # 4. 메인 화면 출력
    # -------------------------------------------------------------------
    st.header(f"🌍 Current Weather Dashboard")
    
    if city:
        data_current = fetch_weather(city, units)
        data_forecast = fetch_forecast(city, units)
    
        if data_current and data_forecast:
            
            st.subheader(f"📍 {data_current['name']}의 현재 날씨")
            col1, col2, col3 = st.columns(3)
            with col1:
                icon_url = f"https://openweathermap.org/img/wn/{data_current['weather'][0]['icon']}@2x.png"
                st.image(icon_url, width=80, caption=f"{data_current['weather'][0]['description']}")
            with col2:
                st.metric("기온", f"{data_current['main']['temp']}{unit_symbol}")
                st.write(f"체감온도: {data_current['main']['feels_like']}{unit_symbol}")
            with col3:
                st.metric("습도", f"{data_current['main']['humidity']}%")
                st.write(f"기압: {data_current['main']['pressure']} hPa")
    
            st.divider()
    
            st.subheader("🌡 3시간 간격 기온 예보 (Plotly)")
            try:
                forecast_data = [(item['dt_txt'], item['main']['temp']) for item in data_forecast['list']]
                df = pd.DataFrame(forecast_data, columns=['Time', 'Temperature'])
                df['Time'] = pd.to_datetime(df['Time'])
                fig = px.line(df, x='Time', y='Temperature', title=f"{data_current['name']} 기온 변화", labels={'Time': '시간', 'Temperature': f'기온 ({unit_symbol})'})
                fig.update_traces(mode='lines+markers', line_shape='spline')
                st.plotly_chart(fig, use_container_width=True)
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
                    get_color='[200, 30, 0, 160]', # RGBA (빨간색)
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
                        map_style='mapbox://styles/mapbox/light-v9', # Mapbox 스타일
                        api_keys={'mapbox': mapbox_key}, 
                        tooltip={"text": f"{data_current['name']}\nLat: {lat}, Lon: {lon}"}
                    )
                    st.pydeck_chart(r)
                else:
                    # 키가 없으면 경고 메시지를 표시합니다.
                    st.warning("🗺️ Mapbox API 키가 .streamlit/secrets.toml에 설정되지 않아 지도를 표시할 수 없습니다.")
            
            except Exception as e:
                st.error(f"Pydeck 맵 생성 중 오류 발생: {e}")
    
        else:
            st.error(f"❌ 도시 '{city}'의 날씨 정보를 불러오는 데 실패했습니다. 도시 이름을 확인하거나 다시 시도해주세요.")
    else:
        st.info("왼쪽 사이드바에서 도시를 선택하거나 직접 검색해주세요 🌏")