import io
from datetime import datetime

import folium
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image, ImageChops, ImageEnhance
from streamlit_folium import st_folium

st.set_page_config(
    page_title="SafeNova | Construction Intelligence",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- Styling --------------------------------------
st.markdown("""
<style>
    .stApp { background: #f4f7fb; }
    [data-testid="stSidebar"] { background: #101d32; }
    [data-testid="stSidebar"] * { color: #e8eef8 !important; }
    .hero {
        padding: 1.45rem 1.7rem; border-radius: 18px;
        background: linear-gradient(120deg, #10233f, #176b69);
        color: white; margin-bottom: 1rem;
    }
    .hero h1 { color: white; margin: 0; font-size: 2rem; }
    .hero p { color: #d7e9ed; margin: .45rem 0 0 0; }
    .metric-card {
        background: white; border: 1px solid #e1e8f0;
        border-radius: 14px; padding: 1rem 1.1rem;
        min-height: 112px;
    }
    .metric-label { color: #627188; font-size: .84rem; }
    .metric-value { color: #14263f; font-size: 1.8rem; font-weight: 750; }
    .metric-note { color: #728096; font-size: .76rem; }
    .section-note { color: #64748b; font-size: .9rem; }
    div[data-testid="stMetric"] {
        background: white; padding: 14px 16px; border-radius: 12px;
        border: 1px solid #e1e8f0;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 9px; padding: 8px 14px; }
</style>
""", unsafe_allow_html=True)

# ----------------------------- Sidebar --------------------------------------
with st.sidebar:
    st.markdown("## 🏗️ SafeNova")
    st.caption("AI + GIS CONSTRUCTION MONITORING")
    st.divider()
    page = st.radio(
        "WORKSPACE",
        ["Overview", "Satellite Comparison", "Terrain & Soil", "Approval Verification", "GIS Monitoring", "Alerts", "Reports"],
        index=0,
    )
    st.divider()
    st.markdown("**Monitoring area**")
    area = st.selectbox("Area", ["Tambaram, Chennai", "Chennai (demo)", "Custom image test"])
    st.markdown("**Analysis settings**")
    threshold = st.slider("Pixel difference threshold", 10, 100, 30, 5)
    st.caption("This prototype uses image-pixel screening, not a trained AI model.")
    st.divider()
    st.caption("SafeNova • Student demonstration prototype")

# ----------------------------- Data -----------------------------------------
# These are illustrative demo records only; not official municipal data.
alerts = pd.DataFrame([
    {"Case ID": "SN-001", "Location": "Tambaram — Demo Site A", "Priority": "High",
     "Status": "Needs review", "Latitude": 12.9249, "Longitude": 80.1000, "Change": "High pixel variation"},
    {"Case ID": "SN-002", "Location": "Tambaram — Demo Site B", "Priority": "Medium",
     "Status": "Pending review", "Latitude": 12.9300, "Longitude": 80.1150, "Change": "Moderate pixel variation"},
    {"Case ID": "SN-003", "Location": "Tambaram — Demo Site C", "Priority": "Low",
     "Status": "Queued", "Latitude": 12.9170, "Longitude": 80.0900, "Change": "Low pixel variation"},
    {"Case ID": "SN-004", "Location": "Tambaram — Demo Site D", "Priority": "Medium",
     "Status": "Pending review", "Latitude": 12.9400, "Longitude": 80.1050, "Change": "Moderate pixel variation"},
])

def metric_card(label, value, note):
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
        unsafe_allow_html=True,
    )

def open_image(uploaded):
    if uploaded is None:
        return None
    return Image.open(uploaded).convert("RGB")

def compare_images(before, after, pixel_threshold):
    # Resize the later image to the earlier image's dimensions for a basic demo.
    after_aligned = after.resize(before.size)
    difference = ImageChops.difference(before, after_aligned)
    diff_array = np.asarray(difference)
    changed_mask = np.any(diff_array > pixel_threshold, axis=2)
    changed_pct = float(changed_mask.mean() * 100)
    # Highlight changed pixels in red over the later image.
    base = np.asarray(after_aligned).copy()
    overlay = base.copy()
    overlay[changed_mask] = [239, 68, 68]
    highlighted = Image.blend(Image.fromarray(base), Image.fromarray(overlay), 0.62)
    return after_aligned, difference, highlighted, changed_pct, int(changed_mask.sum()), int(changed_mask.size)

def priority_for(pct):
    if pct >= 20:
        return "High"
    if pct >= 7:
        return "Medium"
    return "Low"

def read_tabular_upload(uploaded):
    """Read an uploaded CSV or Excel file into a dataframe."""
    if uploaded is None:
        return None
    try:
        if uploaded.name.lower().endswith(".csv"):
            return pd.read_csv(uploaded)
        return pd.read_excel(uploaded)
    except Exception as exc:
        st.error(f"Could not read {uploaded.name}: {exc}")
        return None

def normalize_column_names(frame):
    """Normalize column names for more forgiving file matching."""
    out = frame.copy()
    out.columns = [str(col).strip().lower().replace("_", " ").replace("-", " ") for col in out.columns]
    return out

def first_matching_column(frame, candidates):
    for candidate in candidates:
        key = candidate.lower().replace("_", " ").replace("-", " ")
        if key in frame.columns:
            return key
    return None

def compare_approval_files(official, observed):
    """Compare official permit data against field-observed site data."""
    official = normalize_column_names(official)
    observed = normalize_column_names(observed)
    official_id = first_matching_column(official, ["plot id", "plot number", "survey number", "case id", "site id"])
    observed_id = first_matching_column(observed, ["plot id", "plot number", "survey number", "case id", "site id"])
    if not official_id or not observed_id:
        return None, "Both files need a shared identifier column such as Plot ID or Survey Number."
    official = official.rename(columns={official_id: "match_id"})
    observed = observed.rename(columns={observed_id: "match_id"})
    merged = observed.merge(official, on="match_id", how="left", suffixes=("_observed", "_official"), indicator=True)
    results = []
    for _, row in merged.iterrows():
        issues = []
        if row["_merge"] == "left_only":
            issues.append("No matching official record")
        permit_col = first_matching_column(official, ["permit number", "approval number", "permit id"])
        status_col = first_matching_column(official, ["approval status", "status", "permit status"])
        approved_floors = first_matching_column(official, ["approved floors", "permitted floors", "sanctioned floors"])
        observed_floors = first_matching_column(observed, ["observed floors", "actual floors", "constructed floors"])
        approved_use = first_matching_column(official, ["approved use", "permitted use", "land use"])
        observed_use = first_matching_column(observed, ["observed use", "actual use", "current use"])
        if row["_merge"] == "both":
            if permit_col and (pd.isna(row.get(permit_col)) or str(row.get(permit_col)).strip() == ""):
                issues.append("Permit number missing")
            if status_col and str(row.get(status_col, "")).strip().lower() not in ["approved", "valid", "active", "sanctioned"]:
                issues.append("Approval status needs review")
            if approved_floors and observed_floors:
                try:
                    a = pd.to_numeric(pd.Series([row.get(approved_floors)]), errors="coerce").iloc[0]
                    o = pd.to_numeric(pd.Series([row.get(observed_floors)]), errors="coerce").iloc[0]
                    if pd.notna(a) and pd.notna(o) and o > a:
                        issues.append(f"Observed floors ({o:g}) exceed approved floors ({a:g})")
                except Exception:
                    pass
            if approved_use and observed_use:
                a_use = str(row.get(approved_use, "")).strip().lower()
                o_use = str(row.get(observed_use, "")).strip().lower()
                if a_use and o_use and a_use != "nan" and o_use != "nan" and a_use != o_use:
                    issues.append("Observed use differs from approved use")
        results.append({
            "Plot / Survey ID": row.get("match_id", ""),
            "Screening Result": "Potential mismatch — verify" if issues else "No mismatch detected in supplied fields",
            "Evidence / Issues": "; ".join(issues) if issues else "No mismatch found in compared fields",
        })
    return pd.DataFrame(results), None

# Keep comparison outputs available across dashboard pages.
before_file = None
after_file = None
before_img = None
after_img = None
comparison = None

st.markdown(
    '<div class="hero"><h1>SafeNova Construction Intelligence</h1>'
    '<p>Monitor possible construction changes, review flagged locations, and prepare evidence for field verification.</p></div>',
    unsafe_allow_html=True,
)
st.caption("DEMO MODE • Tambaram 2020 vs 2025 is a comparison workspace label; upload actual, aligned imagery to calculate results.")

# Upload controls remain accessible from comparison page; overview gives quick access too.
if page in ["Overview", "Satellite Comparison"]:
    with st.expander("Upload comparison images", expanded=(page == "Satellite Comparison")):
        up1, up2 = st.columns(2)
        with up1:
            before_file = st.file_uploader("Earlier image (e.g., 2020)", type=["png", "jpg", "jpeg", "webp"], key="before_upload")
        with up2:
            after_file = st.file_uploader("Recent image (e.g., 2025)", type=["png", "jpg", "jpeg", "webp"], key="after_upload")
        if before_file and after_file:
            before_img = open_image(before_file)
            after_img = open_image(after_file)
            comparison = compare_images(before_img, after_img, threshold)
            st.success("Images loaded. Pixel screening is ready.")
        else:
            st.info("Upload both images to calculate the changed-pixel percentage and generate a highlighted comparison.")

if page == "Overview":
    st.subheader("Dashboard overview")
    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("MONITORED DEMO SITES", "04", "Illustrative locations")
    with c2: metric_card("HIGH PRIORITY", "01", "Requires first review")
    with c3: metric_card("MEDIUM PRIORITY", "02", "Review queue")
    with c4:
        val = f"{comparison[3]:.2f}%" if comparison else "—"
        metric_card("IMAGE CHANGE", val, "Calculated after image upload")
    st.write("")
    left, right = st.columns([1.35, 1])
    with left:
        st.markdown("### Recent monitoring activity")
        st.dataframe(alerts[["Case ID", "Location", "Priority", "Status"]], hide_index=True, use_container_width=True)
    with right:
        st.markdown("### Priority distribution")
        counts = alerts["Priority"].value_counts().reindex(["High", "Medium", "Low"], fill_value=0)
        st.bar_chart(counts)
    if comparison:
        st.markdown("### Latest image comparison")
        b, a, h = st.columns(3)
        b.image(before_img, caption="Earlier image", use_container_width=True)
        a.image(comparison[0], caption="Recent image (resized for comparison)", use_container_width=True)
        h.image(comparison[2], caption="Highlighted pixel differences", use_container_width=True)
        st.metric("Approximate changed pixels", f"{comparison[3]:.2f}%", help="Percentage of pixels whose RGB difference exceeds the selected threshold.")

elif page == "Satellite Comparison":
    st.subheader("Satellite comparison")
    st.markdown('<p class="section-note">Tambaram • 2020 vs 2025 — upload matching images below. No real satellite imagery is bundled with this demo.</p>', unsafe_allow_html=True)
    if comparison:
        aligned_after, diff, highlighted, pct, changed, total = comparison
        x1, x2 = st.columns(2)
        x1.image(before_img, caption="BEFORE • Earlier image", use_container_width=True)
        x2.image(aligned_after, caption="AFTER • Recent image", use_container_width=True)
        st.divider()
        d1, d2 = st.columns(2)
        d1.image(highlighted, caption="Changed areas highlighted in red", use_container_width=True)
        d2.image(diff, caption="Raw pixel-difference image", use_container_width=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("Changed pixels", f"{pct:.2f}%")
        m2.metric("Pixel count", f"{changed:,}")
        m3.metric("Pixels compared", f"{total:,}")
        priority = priority_for(pct)
        st.info(f"Suggested review priority: **{priority}**. This is a configurable demo rule, not a legal determination.")
    else:
        st.info("Upload an earlier and a recent image in the panel above to view before/after images, pixel-change percentage, and highlighted differences.")

elif page == "Terrain & Soil":
    st.subheader("Elevation, slope & soil screening")
    st.markdown('<p class="section-note">Upload a site survey CSV or Excel file. This screen identifies terrain and geotechnical factors for engineering review; it does not determine construction legality.</p>', unsafe_allow_html=True)
    st.markdown("**Expected columns:** Site ID, Latitude, Longitude, Elevation (m), Slope (degrees), Soil Type, Bearing Capacity (kPa), Flood Risk")
    terrain_file = st.file_uploader("Upload elevation and soil data (.csv, .xlsx)", type=["csv", "xlsx"], key="terrain_upload")
    if terrain_file:
        terrain = read_tabular_upload(terrain_file)
        if terrain is not None:
            st.dataframe(terrain, hide_index=True, use_container_width=True)
            normalized = normalize_column_names(terrain)
            risk_notes = []
            slope_col = first_matching_column(normalized, ["slope degrees", "slope", "slope deg"])
            flood_col = first_matching_column(normalized, ["flood risk", "flood zone", "flood prone"])
            bearing_col = first_matching_column(normalized, ["bearing capacity kpa", "bearing capacity", "soil bearing capacity kpa"])
            for idx, row in normalized.iterrows():
                issues = []
                if slope_col:
                    slope = pd.to_numeric(pd.Series([row.get(slope_col)]), errors="coerce").iloc[0]
                    if pd.notna(slope) and slope >= 15:
                        issues.append("Steep slope — engineering review")
                if flood_col and str(row.get(flood_col, "")).strip().lower() in ["high", "yes", "true", "flood-prone", "flood prone"]:
                    issues.append("Flood-risk flag — verify with official hazard maps")
                if bearing_col:
                    bearing = pd.to_numeric(pd.Series([row.get(bearing_col)]), errors="coerce").iloc[0]
                    if pd.notna(bearing) and bearing < 100:
                        issues.append("Low reported bearing capacity — geotechnical review")
                risk_notes.append({
                    "Row": idx + 1,
                    "Screening Note": "; ".join(issues) if issues else "No trigger in configured screening rules",
                })
            st.markdown("### Screening notes")
            st.dataframe(pd.DataFrame(risk_notes), hide_index=True, use_container_width=True)
            st.download_button("Download terrain screening notes (CSV)", pd.DataFrame(risk_notes).to_csv(index=False).encode("utf-8"), "safenova_terrain_screening.csv", "text/csv")
    else:
        st.info("No real elevation or soil dataset is bundled with this demo. Upload verified survey data to run screening.")
    st.warning("Elevation and soil flags are engineering/planning indicators, not proof of an unauthorized building. Use official terrain, flood, and geotechnical sources.")

elif page == "Approval Verification":
    st.subheader("Government approval file comparison")
    st.markdown('<p class="section-note">Compare an official permit register with observed site-inspection data. Use CSV or Excel files with a shared Plot ID, Survey Number, Case ID, or Site ID.</p>', unsafe_allow_html=True)
    st.markdown("**Official file columns may include:** Plot ID, Permit Number, Approval Status, Approved Floors, Approved Use.")
    st.markdown("**Observed file columns may include:** Plot ID, Observed Floors, Observed Use.")
    official_file = st.file_uploader("Upload official government approval register (.csv, .xlsx)", type=["csv", "xlsx"], key="official_approval_upload")
    observed_file = st.file_uploader("Upload observed / inspection records (.csv, .xlsx)", type=["csv", "xlsx"], key="observed_site_upload")
    if official_file and observed_file:
        official_data = read_tabular_upload(official_file)
        observed_data = read_tabular_upload(observed_file)
        if official_data is not None and observed_data is not None:
            st.markdown("### File preview")
            preview_left, preview_right = st.columns(2)
            with preview_left:
                st.caption("Official approval register")
                st.dataframe(official_data.head(10), hide_index=True, use_container_width=True)
            with preview_right:
                st.caption("Observed site records")
                st.dataframe(observed_data.head(10), hide_index=True, use_container_width=True)
            results, error = compare_approval_files(official_data, observed_data)
            if error:
                st.error(error)
            elif results is not None:
                st.markdown("### Comparison results")
                st.dataframe(results, hide_index=True, use_container_width=True)
                possible = int(results["Screening Result"].str.startswith("Potential mismatch").sum())
                a, b = st.columns(2)
                a.metric("Sites requiring verification", possible)
                b.metric("Sites compared", len(results))
                st.download_button("Download approval comparison (CSV)", results.to_csv(index=False).encode("utf-8"), "safenova_approval_comparison.csv", "text/csv")
                if possible:
                    st.warning("Potential mismatches were found. They are not a legal finding; verify original records, property identity, dates, and applicable local rules.")
                else:
                    st.success("No mismatches were detected in the supplied fields. This does not guarantee legal compliance.")
    else:
        st.info("Upload both files to compare the official approval records with observed site data.")
    st.caption("Privacy note: only upload records you are authorized to use. For a reliable determination, preserve document dates, issuing authority, plot identity, and audit trail.")

elif page == "GIS Monitoring":
    st.subheader("GIS monitoring map")
    st.markdown('<p class="section-note">Markers are fictional demo locations around Tambaram; they do not represent confirmed violations or official municipal records.</p>', unsafe_allow_html=True)
    selected_priority = st.multiselect("Show priorities", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])
    filtered = alerts[alerts["Priority"].isin(selected_priority)]
    map_obj = folium.Map(location=[12.927, 80.103], zoom_start=13, tiles="OpenStreetMap")
    colors = {"High": "red", "Medium": "orange", "Low": "green"}
    for _, row in filtered.iterrows():
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=9 if row["Priority"] == "High" else 7,
            color=colors[row["Priority"]],
            fill=True,
            fill_opacity=0.8,
            popup=f'{row["Case ID"]} • {row["Priority"]} • {row["Status"]}',
            tooltip=row["Location"],
        ).add_to(map_obj)
    st_folium(map_obj, use_container_width=True, height=480, returned_objects=[])
    st.dataframe(filtered[["Case ID", "Location", "Priority", "Status", "Change"]], hide_index=True, use_container_width=True)

elif page == "Alerts":
    st.subheader("Review priority alerts")
    st.markdown('<p class="section-note">Priorities help organize human review. They do not confirm whether construction is authorized.</p>', unsafe_allow_html=True)
    priority_filter = st.multiselect("Filter by priority", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])
    status_filter = st.multiselect("Filter by status", sorted(alerts["Status"].unique()), default=sorted(alerts["Status"].unique()))
    filtered = alerts[alerts["Priority"].isin(priority_filter) & alerts["Status"].isin(status_filter)]
    st.dataframe(filtered, hide_index=True, use_container_width=True)
    st.markdown("### Review guidance")
    st.markdown("- **High:** review first and arrange verification when appropriate.\n- **Medium:** examine imagery and available approval records.\n- **Low:** keep in the routine monitoring queue.")
    st.warning("An alert is a screening result only. Authorized officials must verify imagery, location, and approval records before taking action.")

elif page == "Reports":
    st.subheader("Export demonstration report")
    st.markdown('<p class="section-note">Download the illustrative alert register or the current image-comparison summary.</p>', unsafe_allow_html=True)
    st.markdown("### Alert register")
    st.dataframe(alerts, hide_index=True, use_container_width=True)
    st.download_button(
        "⬇ Download alert register (CSV)",
        data=alerts.to_csv(index=False).encode("utf-8"),
        file_name="safenova_demo_alerts.csv",
        mime="text/csv",
        use_container_width=False,
    )
    if comparison:
        aligned_after, diff, highlighted, pct, changed, total = comparison
        report = pd.DataFrame([{
            "Area": area,
            "Earlier image": before_file.name if before_file else "uploaded image",
            "Recent image": after_file.name if after_file else "uploaded image",
            "Pixel threshold": threshold,
            "Changed pixel percentage": round(pct, 4),
            "Changed pixel count": changed,
            "Total pixels compared": total,
            "Suggested review priority": priority_for(pct),
            "Generated at": datetime.now().isoformat(timespec="seconds"),
            "Caveat": "Pixel differences are not proof of construction or illegality; human verification required.",
        }])
        st.markdown("### Current comparison summary")
        st.dataframe(report, hide_index=True, use_container_width=True)
        st.download_button(
            "⬇ Download comparison report (CSV)",
            data=report.to_csv(index=False).encode("utf-8"),
            file_name="safenova_comparison_report.csv",
            mime="text/csv",
        )
        buf = io.BytesIO()
        highlighted.save(buf, format="PNG")
        st.download_button(
            "⬇ Download highlighted difference image",
            data=buf.getvalue(),
            file_name="safenova_highlighted_changes.png",
            mime="image/png",
        )
    else:
        st.info("Upload both comparison images from Overview or Satellite Comparison to enable the comparison report and highlighted-image export.")

st.divider()
st.caption("SafeNova • AI + GIS construction-change screening prototype • All demo locations are illustrative • Human verification required")
