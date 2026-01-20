import streamlit as st
from core import Cuboid, Sphere, calculate_csa, ACUTE_ERV

st.set_page_config(page_title="CSA – Lead Metal Classification", layout="wide")

st.title("CSA – Environmental Classification of Massive Metals")
st.markdown("### Surface Critical Approach (SGH / ADR / CLP)")

# =====================================================
# SIDEBAR – GEOMETRY SELECTION
# =====================================================

st.sidebar.header("Object geometry")

geometry = st.sidebar.selectbox(
    "Select geometry",
    ["Cuboid (ingot)", "Sphere (reference / powder)"]
)

# =====================================================
# INPUT PARAMETERS
# =====================================================

st.header("1. Object parameters")

if geometry == "Cuboid (ingot)":
    col1, col2 = st.columns(2)

    with col1:
        L = st.number_input("Length (mm)", value=535.0)
        W = st.number_input("Width (mm)", value=85.0)
        T = st.number_input("Thickness (mm)", value=75.0)

    with col2:
        mass = st.number_input("Mass (kg)", value=25.0)

    obj = Cuboid(L, W, T, mass)

else:
    d = st.number_input("Diameter (mm)", value=1.0)
    obj = Sphere(d)

SSA_OBJECT = obj.ssa()

# =====================================================
# REFERENCE METAL (1 mm Pb sphere)
# =====================================================

st.header("2. Reference metal (T/Dp basis)")

pb_ref = Sphere(1.0)
SSA_REF = pb_ref.ssa()

st.write(f"**Reference SSA (1 mm Pb sphere):** `{SSA_REF:.4f} mm²/mg`")

# =====================================================
# T/Dp AND ERV
# =====================================================

st.header("3. Ecotoxicology & dissolution")

col3, col4 = st.columns(2)

with col3:
    pH_band = st.selectbox("pH band", list(ACUTE_ERV.keys()))
    ERV = ACUTE_ERV[pH_band]
    st.write(f"**Acute ERV:** {ERV} µg Pb/L")

with col4:
    pb_released = st.number_input(
        "Pb released in T/Dp test (µg/L)",
        value=121.3
    )
    mass_loading = st.selectbox("Mass loading (mg/L)", [1.0, 0.1])

# =====================================================
# CSA CALCULATION
# =====================================================

CSA = calculate_csa(
    ssa_ref=SSA_REF,
    mass_loading=mass_loading,
    pb_released=pb_released,
    erv=ERV
)

# =====================================================
# RESULTS
# =====================================================

st.header("4. Results")

col5, col6, col7 = st.columns(3)

col5.metric("Object SSA (mm²/mg)", f"{SSA_OBJECT:.6f}")
col6.metric("Critical CSA (mm²/mg)", f"{CSA:.4f}")

if SSA_OBJECT > CSA:
    col7.error("ENVIRONMENTALLY HAZARDOUS (UN 3077)")
else:
    col7.success("NOT CLASSIFIED")

# =====================================================
# TRACEABILITY
# =====================================================

with st.expander("Show calculation trace"):
    st.write(f"SAL = SSA_ref × mass_loading = {SSA_REF:.4f} × {mass_loading}")
    st.write(f"CSA = (SAL / Pb_released) × ERV")
