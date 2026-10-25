
import streamlit as st
import numpy as np
import pandas as pd
import folium
from PIL import Image, ImageChops
from streamlit_folium import st_folium

st.set_page_config(
    page_title="SafeNova",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ SafeNova")
st.subheader("AI & GIS-Based Construction Monitoring")
st.info(
    "Student prototype: alerts indicate possible changes "
    "and require human verification."
)

tab1, tab2 = st.tabs([
    "Image Change Screening",
    "GIS Alert Map"
])

with tab1:
    st.header("Compare Construction Images")

    before_file = st.file_uploader(
        "Upload earlier image",
        type=["png", "jpg", "jpeg"],
        key="before"
    )

    after_file = st.file_uploader(
        "Upload recent image",
        type=["png", "jpg", "jpeg"],
        key="after"
    )

    if before_file and after_file:
        before = Image.open(before_file).convert("RGB")
        after = Image.open(after_file).convert("RGB")

        after = after.resize(before.size)

        difference = ImageChops.difference(before, after)
        diff_array = np.array(difference)

        changed_pixels = np.any(diff_array > 30, axis=2)
        change_percentage = (
            changed_pixels.sum() / changed_pixels.size
        ) * 100

        col1, col2 = st.columns(2)

        with col1:
            st.image(before, caption="Earlier Image",
                     use_container_width=True)

        with col2:
            st.image(after, caption="Recent Image",
                     use_container_width=True)

        st.image(
            difference,
            caption="Pixel Difference Visualization",
            use_container_width=True
        )

        st.metric(
            "Approximate Changed Pixels",
            f"{change_percentage:.2f}%"
        )

        st.warning(
            "Pixel differences do not prove construction activity. "
            "Lighting, weather, and camera changes may affect results."
        )

with tab2:
    st.header("Sample Construction Alert Map")

    records = pd.DataFrame([
        {
            "Case": "CASE001",
            "Location": "Sample A",
            "Priority": "High",
            "Latitude": 13.0827,
            "Longitude": 80.2707
        },
        {
            "Case": "CASE002",
            "Location": "Sample B",
            "Priority": "Medium",
            "Latitude": 13.0604,
            "Longitude": 80.2496
        },
        {
            "Case": "CASE003",
            "Location": "Sample C",
            "Priority": "Low",
            "Latitude": 13.0475,
            "Longitude": 80.2090
        }
    ])

    st.caption(
        "All cases are fictional examples. Coordinates are illustrative "
        "and do not identify actual construction violations."
    )

    st.dataframe(records, use_container_width=True)

    construction_map = folium.Map(
        location=[13.06, 80.25],
        zoom_start=12
    )

    for _, record in records.iterrows():
        folium.Marker(
            location=[
                record["Latitude"],
                record["Longitude"]
            ],
            popup=(
                f'{record["Case"]} - {record["Priority"]} '
                "(fictional example)"
            ),
            tooltip=record["Location"]
        ).add_to(construction_map)

    st_folium(
        construction_map,
        width=None,
        height=450,
        use_container_width=True
    )

st.divider()
st.caption(
    "SafeNova | Prototype for construction-change screening "
    "| Human verification required"
)
