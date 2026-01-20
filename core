import math
from dataclasses import dataclass

# =========================
# ERV DATA (µg Pb/L)
# =========================

ACUTE_ERV = {
    "5.5–6.5": 40.8,
    "6.5–7.5": 32.5,
    "7.5–8.5": 20.5
}

CHRONIC_ERV = {
    "5.5": 5.2  # example value
}

# =========================
# GEOMETRIES
# =========================

@dataclass
class Cuboid:
    L_mm: float
    W_mm: float
    T_mm: float
    mass_kg: float

    def surface_mm2(self):
        return 2 * (self.L_mm*self.W_mm + self.W_mm*self.T_mm + self.T_mm*self.L_mm)

    def mass_mg(self):
        return self.mass_kg * 1e6

    def ssa(self):
        return self.surface_mm2() / self.mass_mg()


@dataclass
class Sphere:
    diameter_mm: float
    density_g_cm3: float = 11.35

    def surface_mm2(self):
        r = self.diameter_mm / 2
        return 4 * math.pi * r**2

    def mass_mg(self):
        r_cm = (self.diameter_mm / 10) / 2
        vol_cm3 = 4/3 * math.pi * r_cm**3
        return vol_cm3 * self.density_g_cm3 * 1000

    def ssa(self):
        return self.surface_mm2() / self.mass_mg()


# =========================
# CSA CALCULATION
# =========================

def calculate_csa(ssa_ref, mass_loading, pb_released, erv):
    sal = ssa_ref * mass_loading
    csa_sal = (sal / pb_released) * erv
    return csa_sal / mass_loading
