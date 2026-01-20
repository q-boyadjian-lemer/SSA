import streamlit as st
import numpy as np

st.set_page_config(page_title="CSA – Classification environnementale", layout="wide")
st.title("CSA – Classification environnementale des métaux massifs")
st.markdown("### Approche critique de surface (CSA)")

# =====================================================
# CONSTANTES
# =====================================================
DENSITY_PB = 11.35e-6  # kg/mm³

# =====================================================
# 1. SÉLECTION DE LA GÉOMÉTRIE
# =====================================================
geometry_type = st.radio("Type de géométrie", ["Sphère", "Cuboid", "Libre"])

st.header("2. Paramètres de la géométrie")

if geometry_type == "Sphère":
    diameter = st.number_input("Diamètre (mm)", value=8.0)
    radius = diameter / 2
    volume = 4/3 * np.pi * radius**3
    SA = 4 * np.pi * radius**2

elif geometry_type == "Cuboid":
    L = st.number_input("Longueur (mm)", value=535.0)
    W = st.number_input("Largeur (mm)", value=85.0)
    T = st.number_input("Épaisseur (mm)", value=75.0)
    volume = L * W * T
    SA = 2*(L*W + L*T + W*T)

else:  # Libre
    SA = st.number_input("Surface totale (mm²)", value=183950.0)
    volume = st.number_input("Volume (mm³)", value=25000000.0)

# Masse calculée automatiquement
mass_kg = volume * DENSITY_PB
SSA_object = SA / (mass_kg*1e6)  # mm²/mg

st.write(f"Masse calculée automatiquement : {mass_kg:.4f} kg")
st.write(f"SSA de l'objet : {SSA_object:.6f} mm²/mg")

# =====================================================
# 2. PARAMÈTRES T/Dp
# =====================================================
st.header("3. Paramètres T/Dp")

pb_released = st.number_input("Pb libéré dans T/Dp (µg/L)", value=52.1)
SSA_test = st.number_input("SSA mesurée en test (mm²/mg)", value=0.529)
ERV = st.number_input("ERV (µg/L)", value=6.2)

# Calcul CSA
CSA = (ERV / pb_released) * SSA_test

st.header("4. Résultats")

st.write(f"CSA critique : {CSA:.4f} mm²/mg")

if SSA_object > CSA:
    st.error("Classification environnementale requise")
else:
    st.success("Pas de classification environnementale requise")
