import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import streamlit_authenticator as stauth

# ====== Credentials met hashed wachtwoorden (wachtwoord: school123 voor allemaal) ======
credentials = {
    "usernames": {
        "school1": {"name": "Basisschool De Regenboog", "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXe.WI/1/Aob0gE0i1yU5h/.V9uM7S89w."},
        "school2": {"name": "Montessori Lyceum", "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXe.WI/1/Aob0gE0i1yU5h/.V9uM7S89w."},
        "school3": {"name": "Christelijke School De Ark", "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXe.WI/1/Aob0gE0i1yU5h/.V9uM7S89w."}
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "school_dashboard_cookie",
    "random_signature_key_school_2025",  # Verander dit later naar iets geheims
    cookie_expiry_days=30
)

# ====== Login (klassieke werkende syntax) ======
name, authentication_status, username = authenticator.login("Inloggen bij SchoolSocial", "main")

if authentication_status:
    authenticator.logout("Uitloggen", "sidebar")
    school_naam = credentials["usernames"][username]["name"]

    st.set_page_config(page_title=f"{school_naam} Dashboard", page_icon="🏫", layout="wide")
    st.title(f"🏫 {school_naam} Social Dashboard")
    st.sidebar.success(f"Welkom {name}!")

    # ====== Filters ======
    st.sidebar.header("Filters")
    platform = st.sidebar.selectbox("Kies platform", ["Instagram", "TikTok", "Facebook", "Alle platforms"])

    today = datetime.today().date()
    start_date = st.sidebar.date_input("Startdatum", today - timedelta(days=30))
    end_date = st.sidebar.date_input("Einddatum", today)

    if start_date > end_date:
        st.sidebar.error("Startdatum mag niet na einddatum liggen.")
        periode = [today - timedelta(days=30), today]
    else:
        periode = [start_date, end_date]

    # ====== Mock data (verschilt per school) ======
    dates = pd.date_range(start=periode[0], end=periode[1], freq='D')
    platforms = ["Instagram", "TikTok", "Facebook"]
    base_offset = 0 if "Regenboog" in school_naam else 1200 if "Montessori" in school_naam else 2500

    data = []
    for p in platforms:
        base_followers = 5000 + base_offset
        growth = 70 if p == "TikTok" else 30
        for i, date in enumerate(dates):
            data.append({
                "Date": date,
                "Platform": p,
                "Followers": base_followers + i * growth,
                "Engagement Rate (%)": 3.8 + (i % 7)*0.4 + (1.5 if p == "TikTok" else 0),
                "Reach": 1300 + i * 40 + (i % 4)*150,
                "Likes": 250 + i * 15,
                "Comments": 30 + i * 4,
                "Shares": 18 + i * 2
            })

    df = pd.DataFrame(data)
    df['Weekday'] = df['Date'].dt.day_name()

    if platform != "Alle platforms":
        df = df[df["Platform"] == platform]

    # ====== Metrics & Grafieken & Insights (zoals eerder) ======
    col1, col2, col3, col4 = st.columns(4)
    total_followers = df["Followers"].iloc[-1] if not df.empty else 0
    total_engagement = df["Engagement Rate (%)"].mean() if not df.empty else 0
    total_reach = df["Reach"].sum() if not df.empty else 0
    total_interactions = df[["Likes", "Comments", "Shares"]].sum().sum()

    col1.metric("Totale Followers", f"{int(total_followers):,}")
    col2.metric("Gem. Engagement Rate", f"{total_engagement:.1f}%")
    col3.metric("Totale Reach", f"{int(total_reach):,}")
    col4.metric("Totale Interacties", f"{int(total_interactions):,}")

    st.subheader("Followers groei")
    fig = px.line(df, x="Date", y="Followers", color="Platform")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Engagement Rate")
    fig_eng = px.bar(df, x="Date", y="Engagement Rate (%)", color="Platform")
    st.plotly_chart(fig_eng, use_container_width=True)

    st.subheader("Beste dagen om te posten")
    weekday_eng = df.groupby('Weekday')['Engagement Rate (%)'].mean().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], fill_value=0)
    fig_week = px.bar(x=weekday_eng.index, y=weekday_eng.values)
    st.plotly_chart(fig_week, use_container_width=True)

    st.subheader("📊 Insights")
    if df['Platform'].nunique() > 1:
        best = df.groupby('Platform')['Engagement Rate (%)'].mean().idxmax()
        st.success(f"Sterkste platform: **{best}**")
    st.info("Tip: Video's op TikTok doen het goed bij scholen!")

    st.subheader("📥 Export")
    csv = df.to_csv(index=False).encode()
    st.download_button("Download CSV", csv, "social_data.csv", "text/csv")

    st.caption("Je bent ingelogd – dit is jouw school-dashboard!")

elif authentication_status == False:
    st.error("Verkeerde gebruikersnaam of wachtwoord")
elif authentication_status is None:
    st.warning("Vul je inloggegevens in")

# Testaccounts:
# Gebruikersnaam: school1, school2 of school3
# Wachtwoord: school123 (voor alle drie)
