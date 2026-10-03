"""Calculs scientifiques pour la simulation du chauffage de l'acétone."""

import numpy as np
from scipy.optimize import brentq


# Paramètres de référence
DEFAULT_FEED_FLOW = 38.0  # kg/h
DEFAULT_FEED_TEMPERATURE_C = 10.0  # °C
DEFAULT_PRESSURE_ATM = 1.0  # atm
DEFAULT_FRACTION_1 = 0.40
DEFAULT_FRACTION_2 = 0.60

# Masse molaire de l'acétone
M_ACETONE = 58.08  # g/mol

# Paramètres d'Antoine
A_ANT = 4.41877
B_ANT = 1312.253
C_ANT = -32.445
TMIN_ANT = 259.16  # K
TMAX_ANT = 507.60  # K

# Capacité calorifique du liquide : Cp = a + b*T
CP_A = 1.337  # kJ/(kg.K)
CP_B = 2.7752e-3  # kJ/(kg.K²)

# Chaleur de vaporisation
HVAP_REF = 46.95  # kJ/mol
BETA = 0.2826
TC = 508.2  # K


def c_to_k(temperature_c):
    """Convertit une température de degrés Celsius en kelvins."""
    return temperature_c + 273.15


def k_to_c(temperature_k):
    """Convertit une température de kelvins en degrés Celsius."""
    return temperature_k - 273.15


def psat_acetone(temperature_k):
    """Calcule la pression de vapeur de l'acétone en atm."""
    log_pressure = A_ANT - B_ANT / (temperature_k + C_ANT)
    return 10**log_pressure


def boiling_temperature(pressure_atm):
    """Retourne la température d'ébullition en K à la pression indiquée."""
    if pressure_atm <= 0:
        raise ValueError("La pression doit être strictement positive.")

    def function(temperature_k):
        return psat_acetone(temperature_k) - pressure_atm

    try:
        return brentq(function, TMIN_ANT, TMAX_ANT)
    except ValueError as error:
        pressure_min = psat_acetone(TMIN_ANT)
        pressure_max = psat_acetone(TMAX_ANT)
        raise ValueError(
            "La pression est hors du domaine de validité de l'équation "
            f"d'Antoine ({pressure_min:.4f} à {pressure_max:.2f} atm)."
        ) from error


def cp_liquid(temperature_k):
    """Calcule Cp de l'acétone liquide en kJ/(kg.K)."""
    return CP_A + CP_B * temperature_k


def delta_h_sensible(temperature_1_k, temperature_2_k):
    """Intègre Cp entre deux températures, en kJ/kg."""
    term_1 = CP_A * (temperature_2_k - temperature_1_k)
    term_2 = (CP_B / 2.0) * (temperature_2_k**2 - temperature_1_k**2)
    return term_1 + term_2


def delta_h_vap(temperature_k):
    """Calcule l'enthalpie de vaporisation en kJ/kg."""
    reduced_temperature = temperature_k / TC
    hvap_molar = (
        HVAP_REF
        * np.exp(-BETA * reduced_temperature)
        * (1.0 - reduced_temperature) ** BETA
    )
    return hvap_molar * 1000.0 / M_ACETONE


def simulation(
    feed_flow=DEFAULT_FEED_FLOW,
    feed_temperature_c=DEFAULT_FEED_TEMPERATURE_C,
    pressure_atm=DEFAULT_PRESSURE_ATM,
    fraction_1=DEFAULT_FRACTION_1,
    fraction_2=DEFAULT_FRACTION_2,
):
    """Exécute le bilan matière et le bilan énergétique du procédé."""
    stream_1_flow = feed_flow * fraction_1
    stream_2_flow = feed_flow * fraction_2

    initial_temperature_k = c_to_k(feed_temperature_c)
    boiling_temperature_k = boiling_temperature(pressure_atm)

    sensible_heat = delta_h_sensible(
        initial_temperature_k, boiling_temperature_k
    )
    latent_heat = delta_h_vap(boiling_temperature_k)
    total_heat = sensible_heat + latent_heat

    # Seule la deuxième branche est chauffée.
    duty_kj_h = stream_2_flow * total_heat
    power_kw = duty_kj_h / 3600.0

    outlet_flow = stream_1_flow + stream_2_flow
    mass_balance_error = feed_flow - outlet_flow

    return {
        "debit1": stream_1_flow,
        "debit2": stream_2_flow,
        "Teb_K": boiling_temperature_k,
        "Teb_C": k_to_c(boiling_temperature_k),
        "h_sensible": sensible_heat,
        "h_vaporisation": latent_heat,
        "h_total": total_heat,
        "Q_kJ_h": duty_kj_h,
        "Q_kW": power_kw,
        "debit_sortie": outlet_flow,
        "erreur_bilan": mass_balance_error,
    }


def curve_data():
    """Crée les 25 points pression/température du code scientifique initial."""
    pressure_values = np.linspace(0.1, 3.0, 25)
    temperature_values = np.array(
        [k_to_c(boiling_temperature(pressure)) for pressure in pressure_values]
    )
    return pressure_values, temperature_values
