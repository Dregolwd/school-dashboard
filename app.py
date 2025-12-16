import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import streamlit_authenticator as stauth
import yaml

# ====== Authenticator configuratie met testgebruikers ======
credentials = {
    "usernames": {
        "school1": {
            "email": "school1@demo.nl",
            "name": "Basisschool De Regenboog",
            "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXe.WI/1/Aob0gE0i1yU5h/.V9uM7S89w."  # hashed "school123"
        },
        "school2": {
            "email": "school2@demo.nl",
            "name": "Montessori Lyceum",
            "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXe.WI/1/Aob0gE0i1yU5h/.V9uM7S89w."  # hashed "school123"
        },
        "school3": {
            "email": "school3@demo.nl",
            "name": "Christelijke School De Ark",
            "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXe.WI/1/Aob0gE0i1yU5h/.V9uM7S89w."  # hashed "school123"
        }
    }
}

cookie = {
    'expiry_days': 30,
    'key': 'random_signature_key_for_school_dashboard',  # Vervang later door een geheime sleutel
    'name': 'school_dashboard_cookie'
}

authenticator = stauth.Authenticate(
    credentials,
    cookie['name'],
    cookie['key'],
    cookie['expiry_days']
)

# ====== Login (correcte nieuwe syntax) ======
name, authentication_status, username = authenticator.login(fields={'Form name': 'Inloggen bij SchoolSocial'}, location='main')

if authentication_status:
    # ====== Ingelogd – toon dashboard ======
    school_naam = credentials['usernames'][username]['name']
    st.sidebar.success(f"Welkom {name}!")
    authenticator.logout("Uitloggen", "sidebar")

    st.set_page_config(page_title=f"{school_naam} - Dashboard", page_icon="🏫", layout="wide")
    st.title(f"🏫 {school_naam} Social Dashboard")

    # Sidebar filters
    st.sidebar.header("Filters")
    platform = st.sidebar.selectbox("Kies platform", ["Instagram", "TikTok", "Facebook", "Alle platforms"])

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

    # ====== Mock data (iets anders per school voor realistisch gevoel) ======
    dates = pd.date_range(start=periode[0], end=periode[1], freq='D')
    platforms = ["Instagram", "TikTok", "Facebook"]

    data = []
    base_offset = 0 if "Regenboog" in school_naam else 1500 if "Montessori" in school_naam else 3000
    for p in platforms:
        base_followers = 5000 + base_offset
        growth = 60 if p == "TikTok" else 25
        for i, date in enumerate(dates):
            data.append({
                "Date": date,
                "Platform": p,
                "Followers": base_followers + i * growth,
                "Engagement Rate (%)": 3.5 + (i % 7)*0.4 + (1.2 if p == "TikTok" else 0),
                "Reach": 1200 + i * 35 + (i % 4)*120,
                "Likes": 220 + i * 12,
                "Comments": 25 + i * 3,
                "Shares": 15 + i * 2
            })

    df = pd.DataFrame(data)
    df['Weekday'] = df['Date'].dt.day_name()

    if platform != "Alle platforms":
        df = df[df["Platform"] == platform]

    # ====== Metrics ======
    col1, col2, col3, col4 = st.columns(4)
    total_followers = df["Followers"].iloc[-1] if not df.empty else 0
    total_engagement = df["Engagement Rate (%)"].mean() if not df.empty else 0
    total_reach = df["Reach"].sum() if not df.empty else 0
    total_interactions = df[["Likes", "Comments", "Shares"]].sum().sum()

    col1.metric("Totale Followers", f"{int(total_followers):,}")
    col2.metric("Gem. Engagement Rate", f"{total_engagement:.1f}%")
    col3.metric("Totale Reach", f"{int(total_reach):,}")
    col4.metric("Totale Interacties", f"{int(total_interactions):,}")

    # ====== Grafieken ======
    st.subheader("Followers groei over tijd")
    fig = px.line(df, x="Date", y="Followers", color="Platform", title="Followers ontwikkeling")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Engagement Rate")
    fig_eng = px.bar(df, x="Date", y="Engagement Rate (%)", color="Platform")
    st.plotly_chart(fig_eng, use_container_width=True)

    st.subheader("Reach & Likes")
    fig_reach = go.Figure()
    fig_reach.add_trace(go.Scatter(x=df["Date"], y=df["Reach"], mode='lines+markers', name='Reach'))
    fig_reach.add_trace(go.Bar(x=df["Date"], y=df["Likes"], name='Likes'))
    st.plotly_chart(fig_reach, use_container_width=True)

    # ====== Beste dagen ======
    st.subheader("Beste dagen om te posten")
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_eng = df.groupby('Weekday')['Engagement Rate (%)'].mean().reindex(weekday_order, fill_value=0)
    fig_week = px.bar(x=weekday_eng.index, y=weekday_eng.values, labels={'x': 'Dag', 'y': 'Engagement Rate (%)'})
    st.plotly_chart(fig_week, use_container_width=True)

    # ====== Insights ======
    st.subheader("📊 Automatische Insights & Tips")
    if df['Platform'].nunique() > 1:
        best = df.groupby('Platform')['Engagement Rate (%)'].mean().idxmax()
        st.success(f"Sterkste platform: **{best}**")
    st.info("Tip: Video's op TikTok scoren goed bij scholen!")

    # ====== Export ======
    st.subheader("📥 Exporteer rapport")
    csv = df.to_csv(index=False).encode()
    st.download_button("Download data als CSV", csv, "social_data.csv", "text/csv")

    st.caption("MVP met login – klaar voor echte data per school!")

elif authentication_status is False:
    st.error("Verkeerde gebruikersnaam of wachtwoord")
elif authentication_status is None:
    st.warning("Vul je inloggegevens in")

# Test inloggegevens (wachtwoord voor alle drie: school123)
# - school1 → Basisschool De Regenboog
# - school2 → Montessori Lyceum
# - school3 → Christelijke School De Ark
