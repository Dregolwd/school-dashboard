import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Pagina configuratie
st.set_page_config(page_title="SchoolSocial Dashboard", page_icon="🏫", layout="wide")

# Titel en intro
st.title("🏫 SchoolSocial Dashboard")
st.markdown("""
Welkom bij je social media dashboard voor scholen!  
Hier zie je overzichtelijk hoe je school presteert op Instagram, TikTok en andere platforms.  
*Dit is een MVP met mock data – later koppelen we echte API's.*
""")

# Sidebar voor filters
st.sidebar.header("Filters")
platform = st.sidebar.selectbox("Kies platform", ["Instagram", "TikTok", "Alle platforms"])
periode = st.sidebar.date_range_picker("Selecteer periode", 
                                      default_value=[datetime.today() - timedelta(days=30), datetime.today()])

# Mock data genereren
dates = pd.date_range(start=periode[0], end=periode[1], freq='D')
platforms = ["Instagram", "TikTok", "Facebook"]

data = []
for p in platforms:
    base_followers = 5000 if p == "Instagram" else 3000 if p == "TikTok" else 2000
    for i, date in enumerate(dates):
        data.append({
            "Date": date,
            "Platform": p,
            "Followers": base_followers + i * (50 if p == "TikTok" else 20),  # Groei
            "Engagement Rate (%)": 3.5 + (i % 7) * 0.5,  # Schommeling
            "Reach": 1000 + i * 30 + (i % 5)*100,
            "Likes": 200 + i * 10,
            "Comments": 20 + i * 2,
            "Shares": 10 + i * 1
        })

df = pd.DataFrame(data)

# Filter op platform
if platform != "Alle platforms":
    df = df[df["Platform"] == platform]

# Key metrics bovenaan
col1, col2, col3, col4 = st.columns(4)
total_followers = df["Followers"].iloc[-1] if not df.empty else 0
total_engagement = df["Engagement Rate (%)"].mean() if not df.empty else 0
total_reach = df["Reach"].sum() if not df.empty else 0
total_interactions = df[["Likes", "Comments", "Shares"]].sum().sum()

col1.metric("Totale Followers", f"{int(total_followers):,}")
col2.metric("Gem. Engagement Rate", f"{total_engagement:.1f}%")
col3.metric("Totale Reach", f"{int(total_reach):,}")
col4.metric("Totale Interacties", f"{int(total_interactions):,}")

# Grafieken
st.subheader("Followers groei over tijd")
fig_followers = px.line(df, x="Date", y="Followers", color="Platform", title="Followers ontwikkeling")
st.plotly_chart(fig_followers, use_container_width=True)

st.subheader("Engagement Rate")
fig_eng = px.bar(df, x="Date", y="Engagement Rate (%)", color="Platform", title="Dagelijkse Engagement")
st.plotly_chart(fig_eng, use_container_width=True)

st.subheader("Reach & Interacties")
fig_reach = go.Figure()
fig_reach.add_trace(go.Scatter(x=df["Date"], y=df["Reach"], mode='lines+markers', name='Reach'))
fig_reach.add_trace(go.Bar(x=df["Date"], y=df["Likes"], name='Likes'))
fig_reach.update_layout(title="Reach vs Likes")
st.plotly_chart(fig_reach, use_container_width=True)

# Tabel met top posts (mock)
st.subheader("Top Posts (voorbeeld)")
top_posts = pd.DataFrame({
    "Post": ["Open Dag flyer", "Leerling succesverhaal", "Sportdag video", "Kerstgroet", "Nieuwe inschrijvingen"],
    "Datum": ["2025-12-10", "2025-12-05", "2025-11-28", "2025-11-20", "2025-11-15"],
    "Likes": [450, 380, 620, 290, 510],
    "Comments": [45, 32, 78, 21, 56],
    "Reach": [8500, 7200, 12000, 5400, 9800]
})
st.dataframe(top_posts.style.highlight_max(axis=0), use_container_width=True)

st.markdown("---")
st.caption("MVP gebouwd met ❤️ door jou & Grok – Volgende stap: echte social API's koppelen!")