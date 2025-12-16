import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Pagina configuratie
st.set_page_config(page_title="SchoolSocial Dashboard", page_icon="🏫", layout="wide")

# ====== Sidebar: School personalisatie & filters ======
st.sidebar.header("School instellingen")
school_naam = st.sidebar.text_input("Schoolnaam", value="Jouw Basisschool")
school_logo = st.sidebar.text_input("Logo URL (optioneel)", value="https://via.placeholder.com/150?text=🏫")

if school_logo:
    st.sidebar.image(school_logo, width=150)
st.sidebar.markdown(f"**{school_naam}**")

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

# ====== Titel ======
st.title(f"🏫 {school_naam} Social Dashboard")
st.markdown("""
Welkom bij je social media dashboard voor scholen!  
Hier zie je overzichtelijk hoe je school presteert op Instagram, TikTok en andere platforms.  
*Dit is een MVP met mock data – later echte API's.*
""")

# ====== Mock data (verschilt per schoolnaam) ======
dates = pd.date_range(start=periode[0], end=periode[1], freq='D')
platforms = ["Instagram", "TikTok", "Facebook"]
base_offset = len(school_naam) * 100  # Variatie op basis van naam

data = []
for p in platforms:
    base_followers = 5000 + base_offset
    growth = 80 if p == "TikTok" else 35
    for i, date in enumerate(dates):
        data.append({
            "Date": date,
            "Platform": p,
            "Followers": base_followers + i * growth,
            "Engagement Rate (%)": 4.2 + (i % 7)*0.5 + (2.0 if p == "TikTok" else 0),
            "Reach": 1500 + i * 50 + (i % 4)*180,
            "Likes": 300 + i * 20,
            "Comments": 40 + i * 6,
            "Shares": 25 + i * 4
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
fig = px.line(df, x="Date", y="Followers", color="Platform")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Engagement Rate")
fig_eng = px.bar(df, x="Date", y="Engagement Rate (%)", color="Platform")
st.plotly_chart(fig_eng, use_container_width=True)

st.subheader("Reach & Likes")
fig_reach = go.Figure()
fig_reach.add_trace(go.Scatter(x=df["Date"], y="Reach", mode='lines+markers', name='Reach'))
fig_reach.add_trace(go.Bar(x=df["Date"], y="Likes", name='Likes'))
st.plotly_chart(fig_reach, use_container_width=True)

st.subheader("Beste dagen om te posten")
weekday_eng = df.groupby('Weekday')['Engagement Rate (%)'].mean().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], fill_value=0)
fig_week = px.bar(x=weekday_eng.index, y=weekday_eng.values, labels={'y': 'Engagement Rate (%)'})
st.plotly_chart(fig_week, use_container_width=True)

# ====== Insights & Tips (veilig – geen crash) ======
st.subheader("📊 Insights & Tips")
if df['Platform'].nunique() > 1:
    best = df.groupby('Platform')['Engagement Rate (%)'].mean().idxmax()
    st.success(f"**Sterkste platform:** {best} – focus hier meer op!")

tiktok_df = df[df['Platform'] == 'TikTok']
if not tiktok_df.empty and len(tiktok_df) > 1:
    tiktok_growth = tiktok_df['Followers'].iloc[-1] - tiktok_df['Followers'].iloc[0]
    st.info(f"**TikTok groei:** +{int(tiktok_growth)} followers in deze periode!")

st.info("**Tip:** Video's op TikTok scoren het best bij scholen. Post op dinsdag of donderdag!")

# ====== Export ======
st.subheader("📥 Exporteer je rapport")
csv = df.to_csv(index=False).encode()
st.download_button("Download data als CSV", csv, "social_data.csv", "text/csv")

st.caption("Dashboard klaar voor demo's – volgende stap: echte data of AI met ComfyUI! 🚀")
