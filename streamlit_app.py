import streamlit as st
import numpy as np
import plotly.graph_objects as go
from csa_core import Cuboid, Sphere, calculate_csa, ACUTE_ERV

st.set_page_config(page_title="CSA – Geometry-based Classification", layout="wide")
st.title("CSA – Environmental Classification of Massive Metals")
st.markdown("### Interactive Surface Critical Approach (SGH / ADR)")

# =====================================================
# SIDEBAR – GEOMETRY SELECTION
# =====================================================

st.sidebar.header("1. Geometry selection")

geometry_type = st.sidebar.radio(
    "Select geometry type",
    ["Sphere", "Cube", "Cuboid"]
)

# =====================================================
# INPUT PARAMETERS
# =====================================================

st.header("2. Geometry parameters")

col1, col2 = st.columns([1, 1])

with col1:
    mass_kg = st.slider("Mass (kg)", 0.1, 100.0, 25.0, step=0.1)

    if geometry_type == "Sphere":
        diameter = st.slider("Diameter (mm)", 0.5, 500.0, 50.0)
        geometry = Sphere(diameter_mm=diameter)

    elif geometry_type == "Cube":
        side = st.slider("Side length (mm)", 5.0, 500.0, 100.0)
        geometry = Cuboid(side, side, side, mass_kg)

    else:  # Cuboid
        L = st.slider("Length (mm)", 10.0, 800.0, 535.0)
        W = st.slider("Width (mm)", 10.0, 300.0, 85.0)
        T = st.slider("Thickness (mm)", 10.0, 300.0, 75.0)
        geometry = Cuboid(L, W, T, mass_kg)

# =====================================================
# 3D VISUALIZATION
# =====================================================

with col2:
    st.subheader("3D geometry preview")

    fig = go.Figure()

    if geometry_type == "Sphere":
        u, v = np.mgrid[0:2*np.pi:40j, 0:np.pi:20j]
        r = diameter / 2
        x = r * np.cos(u) * np.sin(v)
        y = r * np.sin(u) * np.sin(v)
        z = r * np.cos(v)

        fig.add_trace(go.Surface(x=x, y=y, z=z, opacity=0.8))

    else:
        if geometry_type == "Cube":
            L = W = T = side

        x = [0, L, L, 0, 0, L, L, 0]
        y = [0, 0, W, W, 0, 0, W, W]
        z = [0, 0, 0, 0, T, T, T, T]

        edges = [
            (0,1),(1,2),(2,3),(3,0),
            (4,5),(5,6),(6,7),(7,4),
            (0,4),(1,5),(2,6),(3,7)
        ]

        for i, j in edges:
            fig.add_trace(go.Scatter3d(
                x=[x[i], x[j]],
                y=[y[i], y[j]],
                z=[z[i], z[j]],
                mode="lines",
                line=dict(width=6)
            ))

    fig.update_layout(
        scene=dict(aspectmode="data"),
        margin=dict(l=0, r=0, b=0, t=0)
    )

    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# CSA CALCULATION
# =====================================================

st.header("3. CSA calculation")

SSA_OBJECT = geometry.ssa()

pb_ref = Sphere(1.0)
SSA_REF = pb_ref.ssa()

col3, col4 = st.columns(2)

with col3:
    pH_band = st.selectbox("pH band", list(ACUTE_ERV.keys()))
    ERV = ACUTE_ERV[pH_band]

with col4:
    pb_released = st.slider("Pb released in T/Dp (µg/L)", 1.0, 500.0, 121.3)
    mass_loading = st.radio("Mass loading (mg/L)", [1.0, 0.1])

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

r1, r2, r3 = st.columns(3)

r1.metric("Object SSA (mm²/mg)", f"{SSA_OBJECT:.6f}")
r2.metric("Critical CSA (mm²/mg)", f"{CSA:.4f}")

if SSA_OBJECT > CSA:
    r3.error("ENVIRONMENTALLY HAZARDOUS (UN 3077)")
else:
    r3.success("NOT CLASSIFIED")

# =====================================================
# TRACEABILITY
# =====================================================

with st.expander("Show calculation details"):
    st.write(f"SSA_object = {SSA_OBJECT:.6f} mm²/mg")
    st.write(f"SSA_reference (1 mm Pb) = {SSA_REF:.4f} mm²/mg")
    st.write("CSA = (SSA_ref × mass_loading / Pb_released) × ERV")
