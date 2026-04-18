import streamlit as st
import math
import folium
import pandas as pd
from streamlit_folium import folium_static
import time
import random
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from streamlit_geolocation import streamlit_geolocation
from twilio.rest import Client
import os

# ------------------ CONFIG ------------------
st.set_page_config(page_title="🚨 Smart Emergency Response System 🚨", layout="wide")

# ------------------ TWILIO CONFIG ------------------
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")

twilio_client = Client(TWILIO_SID, TWILIO_AUTH) if TWILIO_SID else None

# ------------------ DATA ------------------
def get_data():
    hospitals = [
        {"name": "City Hospital", "beds": 2, "total_beds": 50, "lat": 18.5204, "lon": 73.8567, "status": "Available"},
        {"name": "Care Hospital", "beds": 1, "total_beds": 30, "lat": 18.5100, "lon": 73.8200, "status": "Available"},
        {"name": "Metro Hospital", "beds": 0, "total_beds": 40, "lat": 18.5300, "lon": 73.8700, "status": "Full"},
        {"name": "Central Hospital", "beds": 3, "total_beds": 60, "lat": 18.5400, "lon": 73.8500, "status": "Available"}
    ]

    ambulances = [
        {"id": 1, "lat": 18.5150, "lon": 73.8400, "status": "Available"},
        {"id": 2, "lat": 18.5000, "lon": 73.8000, "status": "En Route"},
        {"id": 3, "lat": 18.5250, "lon": 73.8600, "status": "Available"},
        {"id": 4, "lat": 18.5350, "lon": 73.8300, "status": "Available"}
    ]
    return hospitals, ambulances

# ------------------ SESSION STATE ------------------
if "hospitals" not in st.session_state:
    st.session_state.hospitals, st.session_state.ambulances = get_data()

hospitals = st.session_state.hospitals
ambulances = st.session_state.ambulances

# ------------------ FUNCTIONS ------------------
def haversine(lat1, lon1, lat2, lon2):
    return abs(lat1-lat2) + abs(lon1-lon2)

def nearest_ambulance(lat, lon):
    return min(ambulances, key=lambda a: haversine(lat, lon, a["lat"], a["lon"]))

def nearest_hospital(lat, lon):
    available = [h for h in hospitals if h["beds"] > 0]
    return min(available, key=lambda h: haversine(lat, lon, h["lat"], h["lon"])) if available else None

def get_location():
    loc = streamlit_geolocation()
    if loc and "latitude" in loc and loc["latitude"] and loc["latitude"] != 0:
        return loc["latitude"], loc["longitude"]
    return 18.5204, 73.8567

# ------------------ AUTO REFRESH ------------------
st_autorefresh(interval=2000, key="refresh")

# ------------------ GET LOCATION ------------------
lat, lon = get_location()

st.title("🚨 Smart Emergency Response System 🚨")

# ------------------ TABS ------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Control", "Dashboard", "Map", "Analytics", "Admin"]
)

# ------------------ TAB 1 ------------------
with tab1:
    st.subheader("🚨 Control Panel")

    st.write(f"📍 Location: {lat:.4f}, {lon:.4f}")

    if st.button("🚨 Dispatch"):
        amb = nearest_ambulance(lat, lon)
        hosp = nearest_hospital(lat, lon)

        st.success(f"🚑 Ambulance {amb['id']} dispatched")
        if hosp:
            st.info(f"🏥 {hosp['name']}")
        else:
            st.error("No beds available")

    # ------------------ ADVANCED DEMO ------------------
    st.markdown("---")
    st.subheader("🎬 Advanced Live Emergency Simulation")

    # Init states
    if "demo_active" not in st.session_state:
        st.session_state.demo_active = False
    if "demo_progress" not in st.session_state:
        st.session_state.demo_progress = 0
    if "demo_eta" not in st.session_state:
        st.session_state.demo_eta = 10  # seconds

    # Steps
    steps = [
        "📞 Emergency call received",
        "📡 Finding nearest ambulance",
        "🚑 Ambulance dispatched",
        "🚦 Ambulance en route",
        "📍 Reaching location",
        "🏥 Transporting to hospital",
        "✅ Patient admitted"
    ]

    # Start
    if st.button("🚀 Start Advanced Demo"):
        st.session_state.demo_active = True
        st.session_state.demo_progress = 0
        st.session_state.demo_eta = 10

    # Run demo
    if st.session_state.demo_active:

        step = st.session_state.demo_progress

        if step < len(steps):

            # Status
            st.info(steps[step])

            # Progress bar
            st.progress((step + 1) / len(steps))

            # ETA countdown
            st.metric("⏱ ETA (seconds)", st.session_state.demo_eta)

            # Simulate ambulance movement (optional visual)
            if "demo_lat" not in st.session_state:
                st.session_state.demo_lat = lat - 0.01
                st.session_state.demo_lon = lon - 0.01

            # Move ambulance toward user
            st.session_state.demo_lat += (lat - st.session_state.demo_lat) * 0.2
            st.session_state.demo_lon += (lon - st.session_state.demo_lon) * 0.2

            # Show mini map
            demo_map = folium.Map(location=[lat, lon], zoom_start=14)

            folium.Marker(
                [lat, lon],
                tooltip="🚨 Emergency",
                icon=folium.Icon(color="red")
            ).add_to(demo_map)

            folium.Marker(
                [st.session_state.demo_lat, st.session_state.demo_lon],
                tooltip="🚑 Ambulance",
                icon=folium.Icon(color="blue")
            ).add_to(demo_map)

            folium.PolyLine(
                [[st.session_state.demo_lat, st.session_state.demo_lon], [lat, lon]],
                color="blue"
            ).add_to(demo_map)

            folium_static(demo_map, height=300)

            # Update state
            time.sleep(0.8)
            st.session_state.demo_progress += 1
            st.session_state.demo_eta = max(0, st.session_state.demo_eta - 1)

            st.rerun()

        else:
            st.success("🎉 Emergency handled successfully!")
            st.session_state.demo_active = False

    
# ------------------ TAB 2 ------------------
with tab2:
    st.subheader("📊 Dashboard")
    st.metric("Hospitals", len(hospitals))
    st.metric("Ambulances", len(ambulances))
    st.dataframe(pd.DataFrame(hospitals))

# ------------------ TAB 3 ------------------
with tab3:
    st.subheader("🗺️ Map")
    m = folium.Map(location=[lat, lon], zoom_start=14)
    folium.Marker([lat, lon], tooltip="You").add_to(m)

    for a in ambulances:
        folium.Marker([a["lat"], a["lon"]], tooltip=f"A{a['id']}").add_to(m)

    folium_static(m)

# ------------------ TAB 4 ------------------
with tab4:
    st.subheader("📈 Analytics")
    st.plotly_chart(px.bar(pd.DataFrame(hospitals), x="name", y="beds"))

# ------------------ TAB 5 ADMIN ------------------
with tab5:
    st.subheader("📱 Admin Login (OTP)")

    if "otp" not in st.session_state:
        st.session_state.otp = None
        st.session_state.login = False
        st.session_state.sent = False

    mobile = st.text_input("Mobile (+91...)")

    if st.button("Send OTP"):
        if not twilio_client:
            st.error("❌ Twilio not configured (check SID/Auth)")
        elif mobile.startswith("+"):
            otp = str(random.randint(1000, 9999))
            st.session_state.otp = otp

            try:
                message = twilio_client.messages.create(
                    body=f"Your OTP is {otp}",
                    from_=TWILIO_PHONE,
                    to=mobile
                )
                st.success(f"✅ OTP Sent! SID: {message.sid}")
                st.session_state.sent = True

            except Exception as e:
                st.error(f"❌ SMS Failed: {e}")
        else:
            st.error("Enter valid number (+91...)")

    if st.session_state.sent:
        user_otp = st.text_input("Enter OTP")
        if st.button("Verify"):
            if user_otp == st.session_state.otp:
                st.session_state.login = True
                st.success("Logged in")
            else:
                st.error("Wrong OTP")

    if st.session_state.login:
        st.markdown("### 🛠 Admin Panel")

        h_df = pd.DataFrame(hospitals)
        new_h = st.data_editor(h_df)

        if st.button("Save Hospitals"):
            st.session_state.hospitals = new_h.to_dict("records")

        a_df = pd.DataFrame(ambulances)
        new_a = st.data_editor(a_df)

        if st.button("Save Ambulances"):
            st.session_state.ambulances = new_a.to_dict("records")