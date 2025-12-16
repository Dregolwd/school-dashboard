import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# ====== Authenticator setup (test gebruikers) ======
# Dit is een simpele yaml-config met test-users
config = {
    'credentials': {
        'usernames': {
            'school1': {
                'email': 'school1@demo.nl',
                'name': 'Basisschool De Regenboog',
                'password': 'school123'  # In productie hashed!
            },
            'school2': {
                'email': 'school2@demo.nl',
                'name': 'Montessori Lyceum',
                'password': 'school123'
            },
            'school3': {
                'email': 'school3@demo.nl',
                'name': 'Christelijke School De Ark',
                'password': 'school123'
            }
        }
    },
    'cookie': {
        'expiry_days': 30,
        'key': 'random_signature_key',  # Vervang later door een geheime key
        'name': 'school_dashboard_cookie'
    },
    'preauthorized': None
}

# Hashed passwords (voor productie), maar voor nu plain text (werkt alleen lokaal/online met deze lib)
# In echte versie gebruik je stauth.Hasher om wachtwoorden te hashen
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# ====== Login ======
name, authentication_status, username = authenticator.login('Inloggen', 'main')

if authentication_status:
    # ====== Welkom na login ======
    school_naam = config['credentials']['usernames'][username]['name']
    st.sidebar.success(f"Welkom {name}!")
    authenticator.logout('Uitloggen', 'sidebar')

    # Pagina config
    st.set_page_config(page_title=f"{school_naam} Dashboard", page_icon="🏫", layout="wide")
    st.title(f"🏫 {school_naam} Social Dashboard")

    # ====== Filters in sidebar ======
    st.sidebar.header("Filters")
    platform = st.sidebar.selectbox("Kies platform", ["Instagram", "TikTok", "Facebook", "Alle platforms"])

    # Datumselectie
    today = datetime.today().date()
    start_date_default = today - timedelta(days=30)
    end_date_default = today

    start_date = st.sidebar.date_input("Startdatum", value=start_date_default)
    end_date = st.sidebar.date_input("Einddatum", value=end_date_default)

    if start_date > end_date:
        st.sidebar.error("Fout: Startdatum mag niet na einddatum liggen.")
        periode = [end_date_default - timedelta(days=30), end_date_default]
    else:
        periode = [start_date, end_date]

    # ====== Mock data (per school iets anders voor demo) ======
    dates = pd.date_range(start=periode[0], end=periode[1], freq='D')
    platforms = ["Instagram", "TikTok", "Facebook"]

    data = []
    for p in platforms:
        base_followers = 5000 + (1000 if 'Regenboog' in school_naam else 2000 if 'Montessori' in school_naam else 3000)
        growth_factor = 50 if p == "TikTok" else 20
        for i, date in enumerate(dates):
            data.append({
                "Date": date,
                "Platform": p,
                "Followers": base_followers + i * growth_factor + (500 if username == 'school3' else 0),
                "Engagement Rate (%)": 3.5 + (i % 7) * 0.5 + (1 if p == "TikTok" else 0),
                "Reach": 1000 + i * 30 + (i % 5)*100,
                "Likes": 200 + i * 10,
                "Comments": 20 + i * 2,
                "Shares": 10 + i * 1
            })

    df = pd.DataFrame(data)
    df['Weekday'] = df['Date'].dt.day_name()

    if platform != "Alle platforms":
        df = df[df["Platform"] == platform]

    # ====== De rest van je dashboard (metrics, grafieken, etc.) ======
    # (Kopieer hier alles vanaf de key metrics uit de vorige versie)

    col1, col2, col3, col4 = st.columns(4)
    total_followers = df["Followers"].iloc[-1] if not df.empty else 0
    total_engagement = df["Engagement Rate (%)"].mean() if not df.empty else 0
    total_reach = df["Reach"].sum() if not df.empty else 0
    total_interactions = df[["Likes", "Comments", "Shares"]].sum().sum()

    col1.metric("Totale Followers", f"{int(total_followers):,}")
    col2.metric("Gem. Engagement Rate", f"{total_engagement:.1f}%")
    col3.metric("Totale Reach", f"{int(total_reach):,}")
    col4.metric("Totale Interacties", f"{int(total_interactions):,}")

    # Grafieken (zelfde als voorheen)
    st.subheader("Followers groei")
    fig = px.line(df, x="Date", y="Followers", color="Platform")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Engagement Rate")
    fig_eng = px.bar(df, x="Date", y="Engagement Rate (%)", color="Platform")
    st.plotly_chart(fig_eng, use_container_width=True)

    # Voeg hier de rest toe: insights, benchmarks, export, etc. (ik hou het kort voor nu)

    st.success("Je bent ingelogd! Dit zijn jouw schoolgegevens.")
    st.caption("MVP met login – volgende stap: echte social media koppelingen per school!")

elif authentication_status is False:
    st.error('Verkeerde gebruikersnaam of wachtwoord')
elif authentication_status is None:
    st.warning('Vul je inloggegevens in')

# Test accounts:
# - school1 / school123 → Basisschool De Regenboog
# - school2 / school123 → Montessori Lyceum
# - school3 / school123 → Christelijke School De Ark
