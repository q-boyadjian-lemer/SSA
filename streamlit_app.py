import streamlit as st
import numpy as np

# =====================================================
# CONFIGURATION
# =====================================================
st.set_page_config(page_title="CSA – Classification environnementale", layout="wide")

st.title("CSA – Classification environnementale des métaux massifs")

# =====================================================
# CONSTANTES
# =====================================================
DENSITY_PB = 11.35e-6  # kg/mm³ (plomb)

# =====================================================
# 1. GÉOMÉTRIE DE L’OBJET
# =====================================================
st.header("1. Description de l’objet")

geometry_type = st.radio(
    "Type de géométrie",
    ["Sphère", "Parallélépipède (Cuboid)", "Géométrie libre"],
    help="La géométrie sert uniquement à calculer la SSA réelle de l’objet."
)

if geometry_type == "Sphère":
    diameter = st.number_input("Diamètre (mm)", value=8.0)
    r = diameter / 2
    volume = 4/3 * np.pi * r**3
    surface = 4 * np.pi * r**2

elif geometry_type == "Parallélépipède (Cuboid)":
    L = st.number_input("Longueur (mm)", value=535.0)
    W = st.number_input("Largeur (mm)", value=85.0)
    T = st.number_input("Épaisseur (mm)", value=75.0)
    volume = L * W * T
    surface = 2 * (L*W + L*T + W*T)

else:  # Géométrie libre
    surface = st.number_input("Surface totale (mm²)", value=183950.0)
    volume = st.number_input("Volume (mm³)", value=2.2e6)

# Masse et SSA objet
mass_kg = volume * DENSITY_PB
mass_mg = mass_kg * 1e6
SSA_object = surface / mass_mg

st.markdown("#### Propriétés calculées automatiquement")
st.write(f"• Masse de l’objet : **{mass_kg:.4f} kg**")
st.write(f"• SSA de l’objet : **{SSA_object:.6f} mm²/mg**")

# =====================================================
# 2. DONNÉES T/Dp (COMMUNES)
# =====================================================
st.header("2. Données issues des essais T/Dp")

st.markdown("""
Ces données proviennent des essais de relargage normalisés.
Elles sont **indépendantes de la géométrie réelle de l’objet**.
""")

SSA_test = st.number_input(
    "SSA utilisée dans l’essai T/Dp (mm²/mg)",
    value=0.529
)

# =====================================================
# 3. CLASSIFICATION AIGUË
# =====================================================
st.header("3. Classification aiguë (Acute)")

st.info("""
🔹 **Règle réglementaire**  
La classification aiguë est évaluée **uniquement à 1 mg/L**.
""")

ERV_acute = st.number_input("ERV aigu (µg/L)", value=6.2)
Pb_release_1 = st.number_input(
    "Pb libéré dans T/Dp à 1 mg/L (µg/L)",
    value=52.1
)

CSA_acute = (ERV_acute / Pb_release_1) * SSA_test

if SSA_object > CSA_acute:
    acute_result = "Acute 1"
else:
    acute_result = "Non classé (aigu)"

st.write(f"CSA aiguë (1 mg/L) : **{CSA_acute:.4f} mm²/mg**")
st.write(f"➡️ **Résultat aigu : {acute_result}**")

# =====================================================
# 4. CLASSIFICATION CHRONIQUE
# =====================================================
st.header("4. Classification chronique (Chronic)")

st.info("""
🔹 **Règle réglementaire**  
La classification chronique est évaluée à **deux charges massiques** :
- 0,1 mg/L (plus sévère)
- 1 mg/L
""")

ERV_chronic = st.number_input("ERV chronique (µg/L)", value=6.2)

Pb_release_01 = st.number_input(
    "Pb libéré dans T/Dp à 0,1 mg/L (µg/L)",
    value=20.0
)

CSA_chronic_01 = (ERV_chronic / Pb_release_01) * SSA_test
CSA_chronic_1 = (ERV_chronic / Pb_release_1) * SSA_test

if SSA_object > CSA_chronic_01:
    chronic_result = "Chronic 1"
elif SSA_object > CSA_chronic_1:
    chronic_result = "Chronic 2"
else:
    chronic_result = "Non classé (chronique)"

st.write(f"CSA chronique @ 0,1 mg/L : **{CSA_chronic_01:.4f} mm²/mg**")
st.write(f"CSA chronique @ 1 mg/L : **{CSA_chronic_1:.4f} mm²/mg**")
st.write(f"➡️ **Résultat chronique : {chronic_result}**")

# =====================================================
# 5. SYNTHÈSE FINALE
# =====================================================
st.header("5. Synthèse de classification")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Aigu")
    st.metric("Classification", acute_result)

with col2:
    st.subheader("Chronique")
    st.metric("Classification", chronic_result)
