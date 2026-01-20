import streamlit as st
import numpy as np
import plotly.graph_objects as go
from csa_core import Cuboid, Sphere, calculate_csa, ACUTE_ERV

st.set_page_config(page_title="CSA – Classification Environnementale", layout="wide")
st.title("CSA – Classification environnementale des métaux massifs")
st.markdown("### Approche critique de surface interactive (SGH / ADR)")

# =====================================================
# SIDEBAR – SÉLECTION DE LA GÉOMÉTRIE
# =====================================================
st.sidebar.header("1. Sélection de la géométrie")

geometry_type = st.sidebar.radio(
    "Type de géométrie",
    ["Sphère", "Cube", "Cuboid", "Libre"]
)
DENSITY_PB = 11.34e-6  # kg/mm³

# =====================================================
# PARAMÈTRES DE LA GÉOMÉTRIE
# =====================================================
st.header("2. Paramètres de la géométrie")

col1, col2 = st.columns([1,1])

with col1:
    if geometry_type == "Sphère":
        diameter_slider = st.slider("Diamètre (mm)", 0.5, 500.0, 50.0)
        diameter_manual = st.number_input("Ou saisir le diamètre (mm)", value=diameter_slider)
        diameter = diameter_manual
        volume = (4/3) * np.pi * (diameter/2)**3  # mm³
        mass_kg = volume * DENSITY_PB
        geometry = Sphere(diameter_mm=diameter)

    elif geometry_type == "Cube":
        side_slider = st.slider("Longueur du côté (mm)", 5.0, 500.0, 100.0)
        side_manual = st.number_input("Ou saisir la longueur du côté (mm)", value=side_slider)
        side = side_manual
        volume = side**3
        mass_kg = volume * DENSITY_PB
        geometry = Cuboid(side, side, side, mass_kg)

    elif geometry_type == "Cuboid":
        L_slider = st.slider("Longueur (mm)", 10.0, 800.0, 535.0)
        L_manual = st.number_input("Ou saisir la longueur (mm)", value=L_slider)
        W_slider = st.slider("Largeur (mm)", 10.0, 300.0, 85.0)
        W_manual = st.number_input("Ou saisir la largeur (mm)", value=W_slider)
        T_slider = st.slider("Épaisseur (mm)", 10.0, 300.0, 75.0)
        T_manual = st.number_input("Ou saisir l'épaisseur (mm)", value=T_slider)

        L, W, T = L_manual, W_manual, T_manual
        volume = L*W*T
        mass_kg = volume * DENSITY_PB
        geometry = Cuboid(L, W, T, mass_kg)

    else:  # Géométrie libre
        SSA = st.number_input("Surface spécifique (mm²/mg)", value=1000.0)
        volume = st.number_input("Volume (mm³)", value=1000.0)
        mass_kg = volume * DENSITY_PB

        class CustomGeometry:
            def __init__(self, ssa, volume, mass):
                self._ssa = ssa
                self.volume = volume
                self.mass = mass
            def ssa(self):
                return self._ssa

        geometry = CustomGeometry(SSA, volume, mass_kg)

st.write(f"Masse calculée automatiquement : {mass_kg:.4f} kg")

# =====================================================
# VISUALISATION 3D
# =====================================================
with col2:
    st.subheader("Aperçu 3D de la géométrie")
    fig = go.Figure()

    if geometry_type == "Sphère":
        u, v = np.mgrid[0:2*np.pi:40j, 0:np.pi:20j]
        r = diameter / 2
        x = r * np.cos(u) * np.sin(v)
        y = r * np.sin(u) * np.sin(v)
        z = r * np.cos(v)
        fig.add_trace(go.Surface(x=x, y=y, z=z, opacity=0.8))

    elif geometry_type in ["Cube", "Cuboid"]:
        if geometry_type == "Cube":
            L = W = T = side
        x = [0, L, L, 0, 0, L, L, 0]
        y = [0, 0, W, W, 0, 0, W, W]
        z = [0, 0, 0, 0, T, T, T, T]
        edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
        for i,j in edges:
            fig.add_trace(go.Scatter3d(x=[x[i], x[j]], y=[y[i], y[j]], z=[z[i], z[j]], mode="lines", line=dict(width=6)))

    else:  # Libre
        fig.add_trace(go.Scatter3d(x=[0,1], y=[0,1], z=[0,1], mode="markers", marker=dict(size=5)))  # Placeholder

    fig.update_layout(scene=dict(aspectmode="data"), margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# CALCUL CSA
# =====================================================
st.header("3. Calcul CSA")

SSA_OBJECT = geometry.ssa()
pb_ref = Sphere(1.0)
SSA_REF = pb_ref.ssa()

col3, col4 = st.columns(2)

with col3:
    pH_band = st.selectbox("Intervalle de pH", list(ACUTE_ERV.keys()))
    ERV = ACUTE_ERV[pH_band]

with col4:
    pb_released_slider = st.slider("Pb libéré en T/Dp (µg/L)", 1.0, 500.0, 121.3)
    pb_released_manual = st.number_input("Ou saisir Pb libéré (µg/L)", value=pb_released_slider)
    pb_released = pb_released_manual

    mass_loading = st.radio("Charge massique (mg/L)", [1.0, 0.1])

CSA = calculate_csa(
    ssa_ref=SSA_REF,
    mass_loading=mass_loading,
    pb_released=pb_released,
    erv=ERV
)

# =====================================================
# RÉSULTATS
# =====================================================
st.header("4. Résultats")
r1, r2, r3 = st.columns(3)

r1.metric("SSA de l'objet (mm²/mg)", f"{SSA_OBJECT:.6f}")
r2.metric("CSA critique (mm²/mg)", f"{CSA:.4f}")

if SSA_OBJECT > CSA:
    r3.error("DANGEREUX POUR L'ENVIRONNEMENT (UN 3077)")
else:
    r3.success("NON CLASSIFIÉ")

# =====================================================
# TRACEABILITY
# =====================================================
with st.expander("Afficher les détails du calcul"):
    st.write(f"SSA_objet = {SSA_OBJECT:.6f} mm²/mg")
    st.write(f"SSA_référence (1 mm Pb) = {SSA_REF:.4f} mm²/mg")
    st.write("CSA = (SSA_ref × charge_massique / Pb_libéré) × ERV")
