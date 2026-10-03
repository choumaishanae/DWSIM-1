"""Interface Streamlit du simulateur de chauffage et vaporisation de l'acétone."""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from calculations import (
    DEFAULT_FEED_FLOW,
    DEFAULT_FEED_TEMPERATURE_C,
    DEFAULT_FRACTION_1,
    DEFAULT_FRACTION_2,
    DEFAULT_PRESSURE_ATM,
    curve_data,
    simulation,
)


st.set_page_config(
    page_title="Simulateur Acétone",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        :root {
            --navy: #15324b;
            --blue: #2b6f8e;
            --teal: #1f9d8b;
            --orange: #e68a32;
            --surface: #f7f9fb;
            --border: #dce5eb;
            --text: #182b3a;
            --muted: #526979;
        }
        html, body, .stApp { color-scheme: light; }
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {
            background: #f3f6f8;
            color: var(--text);
        }
        [data-testid="stHeader"] { background: rgba(243, 246, 248, 0.96); }
        [data-testid="stHeader"] button,
        [data-testid="stHeader"] button span,
        [data-testid="stHeader"] [data-testid="stStatusWidget"],
        [data-testid="stHeader"] [data-testid="stStatusWidget"] span {
            color: #233c4e !important;
        }
        [data-testid="stHeader"] button svg {
            fill: #233c4e !important;
            color: #233c4e !important;
        }
        .main .block-container {
            max-width: 1600px;
            padding-top: 2rem;
            padding-bottom: 2.5rem;
        }
        h1, h2, h3,
        [data-testid="stHeadingWithActionElements"] {
            color: var(--navy) !important;
        }
        p, li, span { color: inherit; }
        .app-subtitle {
            color: var(--muted) !important;
            margin-top: -0.65rem;
            margin-bottom: 1.7rem;
        }
        [data-testid="stSidebar"] {
            background: #ffffff;
            color: var(--text);
            border-right: 1px solid var(--border);
        }
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label {
            color: var(--text) !important;
        }
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
            color: var(--muted) !important;
        }
        [data-testid="stWidgetLabel"] p {
            color: #233c4e !important;
            font-weight: 600;
        }
        [data-testid="stNumberInput"] [data-baseweb="input"],
        [data-testid="stNumberInput"] [data-baseweb="input"] > div,
        [data-testid="stNumberInput"] input {
            background: #ffffff !important;
            border-color: #aabcc8 !important;
        }
        [data-testid="stNumberInput"] input {
            color: #142b3c !important;
            -webkit-text-fill-color: #142b3c !important;
            caret-color: #142b3c;
        }
        [data-testid="stNumberInput"] button {
            background: #edf3f6 !important;
            color: #26485e !important;
            border-color: #aabcc8 !important;
        }
        [data-testid="stNumberInput"] button svg {
            fill: #26485e !important;
        }
        [data-testid="stSidebar"] hr { border-color: var(--border); }
        .section-title {
            font-size: 1.12rem; font-weight: 750; color: var(--navy) !important;
            margin: 1.35rem 0 0.75rem;
        }
        div[data-testid="stMetric"] {
            background: white; border: 1px solid var(--border); border-radius: 12px;
            padding: 1rem 1.1rem; box-shadow: 0 2px 8px rgba(21, 50, 75, 0.05);
        }
        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricLabel"] p,
        div[data-testid="stMetricLabel"] span,
        div[data-testid="stMetricLabel"] * {
            color: #40596a !important;
            font-weight: 650;
            opacity: 1 !important;
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: clip !important;
        }
        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] > div,
        div[data-testid="stMetricValue"] * {
            color: var(--navy) !important;
            opacity: 1 !important;
        }
        div[data-testid="stMetricValue"] > div {
            font-size: clamp(1.2rem, 1.8vw, 1.8rem);
            line-height: 1.2;
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: clip !important;
        }
        .process-wrap {
            background: white; border: 1px solid var(--border); border-radius: 14px;
            padding: 1.35rem; box-shadow: 0 2px 8px rgba(21, 50, 75, 0.05);
        }
        .process-flow {
            display: flex; align-items: center; justify-content: center;
            gap: 0.65rem; flex-wrap: wrap;
        }
        .unit {
            background: #edf5f8; border: 1px solid #bcd4df; color: var(--navy);
            border-radius: 10px; min-width: 118px; padding: 0.85rem 1rem;
            text-align: center; font-weight: 700;
        }
        .unit.feed { background: #eaf3f8; border-color: #a8c9d9; }
        .unit.splitter { background: #f1eef8; border-color: #c9bfe0; }
        .unit.accent { background: #fff3e7; border-color: #efc08f; }
        .unit.product { background: #eaf7f4; border-color: #9fd7cd; }
        .arrow { color: var(--blue); font-size: 1.45rem; font-weight: 700; }
        .split-streams { display: flex; flex-direction: column; gap: 0.35rem; }
        .stream {
            background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
            padding: 0.36rem 0.7rem; color: #425d70; font-size: 0.87rem;
        }
        .balance-ok, .balance-error {
            padding: 1rem 1.1rem; border-radius: 10px; font-weight: 650;
        }
        .balance-ok { background: #e8f6f1; color: #14715f; border: 1px solid #9bd7c9; }
        .balance-error { background: #fff0ef; color: #a63b35; border: 1px solid #efb6b1; }
        .note {
            background: #eef4f7; border-left: 4px solid var(--blue); border-radius: 6px;
            color: #496273; padding: 0.8rem 1rem; font-size: 0.9rem;
        }
        [data-testid="stDataFrame"] { color: var(--text); }
        @media (max-width: 900px) {
            .main .block-container { padding-left: 1rem; padding-right: 1rem; }
            .process-flow { gap: 0.5rem; }
            .unit { min-width: 105px; padding: 0.75rem 0.8rem; }
            [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
                flex: 1 1 45% !important;
                min-width: 210px !important;
            }
        }
        @media (max-width: 620px) {
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
                flex-basis: 100% !important;
                min-width: 100% !important;
            }
        }
        footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


def metric_card(column, label, value, unit):
    """Affiche une mesure avec une unité homogène."""
    column.metric(label, f"{value:,.2f} {unit}")


with st.sidebar:
    st.title("Paramètres")
    st.caption("Conditions opératoires et séparation")

    feed_flow = st.number_input(
        "Débit d'alimentation (kg/h)",
        min_value=0.01,
        value=DEFAULT_FEED_FLOW,
        step=1.0,
        format="%.2f",
    )
    feed_temperature_c = st.number_input(
        "Température d'alimentation (°C)",
        value=DEFAULT_FEED_TEMPERATURE_C,
        step=1.0,
        format="%.2f",
    )
    pressure_atm = st.number_input(
        "Pression (atm)",
        min_value=0.01,
        max_value=30.0,
        value=DEFAULT_PRESSURE_ATM,
        step=0.1,
        format="%.2f",
    )

    st.divider()
    st.subheader("Répartition au splitter")
    fraction_1 = st.number_input(
        "Fraction courant 1",
        min_value=0.0,
        max_value=1.0,
        value=DEFAULT_FRACTION_1,
        step=0.05,
        format="%.2f",
    )
    fraction_2 = st.number_input(
        "Fraction courant 2",
        min_value=0.0,
        max_value=1.0,
        value=DEFAULT_FRACTION_2,
        step=0.05,
        format="%.2f",
    )
    fraction_sum = fraction_1 + fraction_2
    fractions_valid = abs(fraction_sum - 1.0) < 1e-9
    if fractions_valid:
        st.success("Fractions valides : somme = 1,00")
    else:
        st.error(f"Somme actuelle : {fraction_sum:.2f}. Elle doit être égale à 1,00.")


st.title("Simulateur de chauffage de l'acétone")
st.markdown(
    '<p class="app-subtitle">Séparation du débit, chauffage du courant 2 et vaporisation à la pression du procédé.</p>',
    unsafe_allow_html=True,
)

if not fractions_valid:
    st.warning(
        "Ajustez les fractions dans la barre latérale pour lancer la simulation. "
        "Les résultats ne sont affichés que lorsque fraction 1 + fraction 2 = 1."
    )
    st.stop()

try:
    results = simulation(
        feed_flow=feed_flow,
        feed_temperature_c=feed_temperature_c,
        pressure_atm=pressure_atm,
        fraction_1=fraction_1,
        fraction_2=fraction_2,
    )
except ValueError as error:
    st.error(str(error))
    st.stop()

st.markdown('<div class="section-title">Schéma du procédé</div>', unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="process-wrap">
      <div class="process-flow">
        <div class="unit feed">Alimentation<br><small>{feed_flow:.2f} kg/h</small></div>
        <div class="arrow">→</div>
        <div class="unit splitter">Splitter</div>
        <div class="arrow">→</div>
        <div class="split-streams">
          <div class="stream">Courant 1 · {results['debit1']:.2f} kg/h</div>
          <div class="stream">Courant 2 · {results['debit2']:.2f} kg/h</div>
        </div>
        <div class="arrow">→</div>
        <div class="unit accent">Heater<br><small>courant 2</small></div>
        <div class="arrow">→</div>
        <div class="unit product">Vapeur acétone<br><small>{results['Teb_C']:.2f} °C</small></div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-title">Résultats de la simulation</div>', unsafe_allow_html=True)
row_1 = st.columns(3)
metric_card(row_1[0], "Température d'ébullition", results["Teb_C"], "°C")
metric_card(row_1[1], "Débit courant 1", results["debit1"], "kg/h")
metric_card(row_1[2], "Débit courant 2", results["debit2"], "kg/h")

row_2 = st.columns(3)
metric_card(row_2[0], "Chaleur sensible", results["h_sensible"], "kJ/kg")
metric_card(row_2[1], "Chaleur latente", results["h_vaporisation"], "kJ/kg")
metric_card(row_2[2], "Chaleur totale", results["h_total"], "kJ/kg")

row_3 = st.columns(2)
metric_card(row_3[0], "Duty thermique", results["Q_kJ_h"], "kJ/h")
row_3[1].metric("Puissance", f"{results['Q_kW']:,.3f} kW")

st.markdown('<div class="section-title">Bilan massique</div>', unsafe_allow_html=True)
mass_balance_verified = abs(results["erreur_bilan"]) < 1e-9
balance_class = "balance-ok" if mass_balance_verified else "balance-error"
balance_text = "✓ Bilan vérifié" if mass_balance_verified else "✕ Écart de bilan détecté"
st.markdown(
    f"""
    <div class="{balance_class}">
      {balance_text} — Entrée : {feed_flow:.3f} kg/h · Sortie :
      {results['debit_sortie']:.3f} kg/h · Écart : {results['erreur_bilan']:.3e} kg/h
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-title">Pression et température d’ébullition</div>', unsafe_allow_html=True)
chart_column, table_column = st.columns([1.45, 1])
pressures, temperatures = curve_data()

with chart_column:
    figure, axis = plt.subplots(figsize=(8, 5.5))
    axis.plot(
        pressures,
        temperatures,
        "o-",
        color="darkorange",
        linewidth=1.8,
        markersize=4,
        label="Acétone",
    )
    selected_boiling_temperature_c = results["Teb_C"]
    axis.scatter(
        pressure_atm,
        selected_boiling_temperature_c,
        color="red",
        s=65,
        zorder=3,
        label=f"{pressure_atm:.2f} atm : {selected_boiling_temperature_c:.2f} °C",
    )
    axis.set_xlabel("Pression (atm)")
    axis.set_ylabel("Température d'ébullition (°C)")
    axis.set_title("Courbe d'ébullition de l'acétone")
    axis.grid(linestyle=":", alpha=0.7)
    axis.legend()
    figure.tight_layout()
    st.pyplot(figure, width="stretch")
    plt.close(figure)

with table_column:
    data = pd.DataFrame(
        {
            "Pression (atm)": pressures,
            "Téb (°C)": temperatures,
        }
    )
    st.dataframe(
        data.style.format({"Pression (atm)": "{:.3f}", "Téb (°C)": "{:.2f}"}),
        hide_index=True,
        width="stretch",
        height=420,
    )

st.markdown(
    '<div class="note">La courbe reprend 25 points entre 0,1 et 3,0 atm. '
    "Le duty correspond au chauffage et à la vaporisation du courant 2 uniquement.</div>",
    unsafe_allow_html=True,
)
