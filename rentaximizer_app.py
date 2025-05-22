import streamlit as st
import numpy as np
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="RENTAXIMIZER - Simulateur Immobilier", layout="wide")
st.title("💼 RENTAXIMIZER - Simulateur de Rendement Immobilier")
st.markdown("Optimise ton investissement locatif en testant tous les scénarios !")

st.sidebar.header("📊 Paramètres de simulation")

# --- PARAMÈTRES UTILISATEUR ---
# Investissement
prix_bien = st.sidebar.number_input("Prix du bien (€)", 50000, 1000000, 200000)
frais_notaire = st.sidebar.number_input("Frais de notaire (€)", 0, 50000, 15000)
travaux = st.sidebar.number_input("Travaux (€)", 0, 500000, 30000)
ameublement = st.sidebar.number_input("Ameublement (€)", 0, 30000, 5000)
frais_agence = st.sidebar.number_input("Frais d'agence (€)", 0, 30000, 10000)

# Financement
apport = st.sidebar.number_input("Apport personnel (€)", 0, 1000000, 30000)
duree_credit = st.sidebar.slider("Durée du crédit (ans)", 5, 30, 20)
taux_credit = st.sidebar.slider("Taux d'intérêt (%)", 0.5, 6.0, 2.0)
taux_assurance = st.sidebar.slider("Assurance emprunteur (%)", 0.0, 1.0, 0.3)

# Revenus
loyers_mensuels = st.sidebar.number_input("Loyers mensuels (€)", 100, 10000, 1200)
taux_vacance = st.sidebar.slider("Vacance locative (%)", 0.0, 20.0, 5.0)
revalorisation_loyer = st.sidebar.slider("Revalorisation loyers (%)", 0.0, 5.0, 2.0)

# Charges
charges_annuelles = st.sidebar.number_input("Charges annuelles (€)", 0, 20000, 2000)
taxe_fonciere = st.sidebar.number_input("Taxe foncière (€)", 0, 10000, 1000)
revalorisation_charges = st.sidebar.slider("Inflation charges (%)", 0.0, 5.0, 2.0)

# Sortie
duree_detention = st.sidebar.slider("Durée de détention (ans)", 1, 30, 20)
valorisation_marche = st.sidebar.slider("Appréciation du bien (%/an)", 0.0, 10.0, 2.0)
taux_fiscalite_plusvalue = st.sidebar.slider("Fiscalité sur plus-value (%)", 0.0, 50.0, 19.0)

# --- CALCULS ---
invest_total = prix_bien + frais_notaire + travaux + ameublement + frais_agence
montant_emprunt = invest_total - apport

mensualite = np.pmt(taux_credit / 100 / 12, duree_credit * 12, -montant_emprunt)
mensualite_totale = mensualite + (montant_emprunt * taux_assurance / 100 / 12)

flux = [-apport]
loyers_annuels = loyers_mensuels * 12
charges = charges_annuelles + taxe_fonciere

for annee in range(1, duree_detention + 1):
    revenus = loyers_annuels * (1 - taux_vacance / 100)
    depenses = charges + mensualite_totale * 12
    flux_annuel = revenus - depenses
    flux.append(flux_annuel)
    loyers_annuels *= (1 + revalorisation_loyer / 100)
    charges *= (1 + revalorisation_charges / 100)

# Revente
valeur_revente = prix_bien * ((1 + valorisation_marche / 100) ** duree_detention)
plus_value = valeur_revente - prix_bien
impot_plusvalue = plus_value * (taux_fiscalite_plusvalue / 100)
net_revente = valeur_revente - impot_plusvalue
flux[-1] += net_revente

tri = np.irr(flux)

# --- AFFICHAGE ---
st.subheader("📈 Résultats de la simulation")
col1, col2, col3 = st.columns(3)
col1.metric("Investissement total (€)", f"{invest_total:,.0f}")
col2.metric("Mensualité totale (€)", f"{mensualite_totale:,.0f}")
col3.metric("TRI estimé", f"{tri*100:.2f} %")

# Graphe
st.line_chart(pd.DataFrame({"Flux de trésorerie": flux}, index=range(duree_detention+1)))

# --- EXPORT EXCEL ---
def to_excel(data):
    df = pd.DataFrame({"Année": list(range(len(data))), "Flux de tréso": data})
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Simulation')
    return output.getvalue()

excel_data = to_excel(flux)
st.download_button(
    label="📥 Télécharger les flux en Excel",
    data=excel_data,
    file_name="rentaximizer_simulation.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.caption("RENTAXIMIZER v1.0 - Simulation financière à titre informatif.")
