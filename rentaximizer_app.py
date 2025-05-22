import streamlit as st
import numpy as np
import pandas as pd

# Titre de l'application
st.set_page_config(page_title="RENTAXIMIZER", layout="wide")
st.title("💰 RENTAXIMIZER - Simulateur de rentabilité immobilière complet")

# --- SIDEBAR ---
st.sidebar.header("Paramètres du projet")

# Coûts d'investissement
st.sidebar.subheader("🏗️ Coûts d'investissement")
prix_bien = st.sidebar.number_input("Prix du bien (€)", value=200000)
frais_notaire = st.sidebar.number_input("Frais de notaire (€)", value=16000)
travaux = st.sidebar.number_input("Travaux (€)", value=30000)
ameublement = st.sidebar.number_input("Ameublement (€)", value=5000)

# Financement
st.sidebar.subheader("🏦 Financement")
apport = st.sidebar.number_input("Apport personnel (€)", value=20000)
taux_emprunt = st.sidebar.slider("Taux d'emprunt (%)", 0.5, 5.0, 1.8)
taux_assurance = st.sidebar.slider("Taux assurance (%)", 0.1, 1.0, 0.3)
duree = st.sidebar.slider("Durée du prêt (ans)", 5, 30, 20)

# Revenus locatifs
st.sidebar.subheader("💸 Revenus locatifs")
loyer_mensuel = st.sidebar.number_input("Loyer mensuel brut (€)", value=1000)

# Charges d'exploitation
st.sidebar.subheader("💼 Charges d’exploitation")
charges_copro = st.sidebar.number_input("Charges copropriété annuelles (€)", value=1200)
assurance_pno = st.sidebar.number_input("Assurance PNO (€)", value=200)
taxe_fonciere = st.sidebar.number_input("Taxe foncière (€)", value=1000)
autres_charges = st.sidebar.number_input("Autres charges annuelles (€)", value=800)

# Revente
st.sidebar.subheader("🏁 Hypothèses de sortie")
duree_conservation = st.sidebar.slider("Durée de conservation (ans)", 5, 30, 15)
valeur_revente = st.sidebar.number_input("Prix de revente estimé (€)", value=250000)
frais_revente = st.sidebar.slider("Frais de revente (%)", 0.0, 10.0, 6.0)

# --- CALCULS ---
montant_emprunt = prix_bien + frais_notaire + travaux + ameublement - apport
taux_mensuel = (taux_emprunt + taux_assurance) / 100 / 12
nb_mensualites = duree * 12
mensualite = montant_emprunt * taux_mensuel / (1 - (1 + taux_mensuel) ** -nb_mensualites)

revenu_annuel = loyer_mensuel * 12
charges_annuelles = charges_copro + assurance_pno + taxe_fonciere + autres_charges
cashflow_annuel = revenu_annuel - charges_annuelles - mensualite * 12

# TRI approximatif
flux = [-apport]
for _ in range(duree_conservation):
    flux.append(cashflow_annuel)
valeur_nette = valeur_revente * (1 - frais_revente / 100) - montant_emprunt
flux[-1] += valeur_nette
try:
    tri = np.irr(flux)
except:
    tri = 0.0

# --- AFFICHAGE DES RÉSULTATS ---
st.subheader("📊 Résultats de la simulation")
col1, col2, col3 = st.columns(3)

col1.metric("Mensualité", f"{mensualite:.0f} €")
col2.metric("Cashflow annuel", f"{cashflow_annuel:.0f} €")
col3.metric("TRI estimé", f"{tri*100:.2f} %")

# Graphique flux de trésorerie
st.subheader("📈 Flux de trésorerie projetés")
df_flux = pd.DataFrame({
    "Année": list(range(duree_conservation + 1)),
    "Flux": flux
})
st.bar_chart(df_flux.set_index("Année"))

# Téléchargement Excel
st.subheader("📥 Export des données")
df_export = pd.DataFrame({
    "Paramètre": ["Prix bien", "Frais notaire", "Travaux", "Ameublement", "Apport", "Montant emprunt", "Mensualité", "Revenus annuels", "Charges annuelles", "Cashflow annuel", "TRI", "Valeur revente nette"],
    "Valeur": [prix_bien, frais_notaire, travaux, ameublement, apport, montant_emprunt, mensualite, revenu_annuel, charges_annuelles, cashflow_annuel, tri, valeur_nette]
})

@st.cache_data
def convert_df(df):
    return df.to_excel(index=False, engine='xlsxwriter')

excel_data = convert_df(df_export)
st.download_button("📤 Télécharger l'analyse (Excel)", data=excel_data, file_name="rentaximizer_resultats.xlsx")
