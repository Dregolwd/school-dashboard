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

# Datumselectie (veilig)
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

# ====== Titel ======
st.title(f"🏫 {school_naam} Social Dashboard")
st.markdown("""
Welkom bij je social media dashboard voor scholen!  
Hier zie je overzichtelijk hoe je school presteert op Instagram, TikTok en andere platforms.  
*Dit is een MVP met mock data – later koppelen we echte API's.*
""")

# ====== Mock data genereren ======
dates = pd.date_range(start=periode[0], end=periode[1], freq='D')
platforms = ["Instagram", "TikTok", "Facebook"]

data = []
for p in platforms:
    base_followers = 5000 if p == "Instagram" else 3000 if p == "TikTok" else 2000
    for i, date in enumerate(dates):
        data.append({
            "Date": date,
            "Platform": p,
            "Followers": base_followers + i * (50 if p == "TikTok" else 20),
            "Engagement Rate (%)": 3.5 + (i % 7) * 0.5 + (1 if p == "TikTok" else 0),
            "Reach": 1000 + i * 30 + (i % 5)*100,
            "Likes": 200 + i * 10,
            "Comments": 20 + i * 2,
            "Shares": 10 + i * 1
        })

df = pd.DataFrame(data)

# Extra kolommen
df['Weekday'] = df['Date'].dt.day_name()
df['Hour'] = (df['Date'].dt.hour + 10) % 24  # Mock posts tussen 10-18 uur

# Filter op platform
if platform != "Alle platforms":
    df = df[df["Platform"] == platform]

# ====== Key metrics ======
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
fig_followers = px.line(df, x="Date", y="Followers", color="Platform", title="Followers ontwikkeling")
st.plotly_chart(fig_followers, use_container_width=True)

st.subheader("Engagement Rate")
fig_eng = px.bar(df, x="Date", y="Engagement Rate (%)", color="Platform", title="Dagelijkse Engagement")
st.plotly_chart(fig_eng, use_container_width=True)

st.subheader("Reach & Likes")
fig_reach = go.Figure()
fig_reach.add_trace(go.Scatter(x=df["Date"], y=df["Reach"], mode='lines+markers', name='Reach'))
fig_reach.add_trace(go.Bar(x=df["Date"], y=df["Likes"], name='Likes'))
fig_reach.update_layout(title="Reach vs Likes")
st.plotly_chart(fig_reach, use_container_width=True)

# ====== Beste postdagen ======
st.subheader("Beste dagen om te posten")
weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
weekday_eng = df.groupby('Weekday')['Engagement Rate (%)'].mean().reindex(weekday_order, fill_value=0)
fig_weekday = px.bar(x=weekday_eng.index, y=weekday_eng.values,
                     title="Gemiddelde Engagement per Weekdag",
                     labels={'x': 'Dag', 'y': 'Engagement Rate (%)'})
st.plotly_chart(fig_weekday, use_container_width=True)

# ====== Insights & Tips (nu veilig) ======
st.subheader("📊 Automatische Insights & Tips")

# Beste en slechtste platform (alleen als er meerdere platforms zijn)
if df['Platform'].nunique() > 1:
    best_platform = df.groupby('Platform')['Engagement Rate (%)'].mean().idxmax()
    worst_platform = df.groupby('Platform')['Engagement Rate (%)'].mean().idxmin()
    st.success(f"**Sterkste platform:** {best_platform} – focus hier meer op!")
    st.warning(f"**Verbeterpunt:** {worst_platform} heeft lagere engagement.")
else:
    st.info("**Tip:** Kies 'Alle platforms' om vergelijkingen tussen platforms te zien.")

# TikTok groei (alleen als TikTok in de data zit)
tiktok_df = df[df['Platform'] == 'TikTok']
if not tiktok_df.empty and len(tiktok_df) > 1:
    tiktok_growth = tiktok_df['Followers'].iloc[-1] - tiktok_df['Followers'].iloc[0]
    st.info(f"**TikTok groeit hard:** +{int(tiktok_growth)} followers in deze periode!")
else:
    st.info("**Tip:** TikTok data wordt getoond bij 'Alle platforms' of als je TikTok selecteert.")

st.info("**Algemene tip:** Post meer video's op dinsdag en donderdag rond 15-17 uur voor maximaal bereik (op basis van mock data).")

# ====== Benchmark vergelijking ======
st.subheader("📈 Hoe doe je het t.o.v. gemiddelde scholen?")
avg_reach_per_post = total_reach / len(df) if len(df) > 0 else 0
benchmark_data = {
    "Metric": ["Gem. Engagement Rate", "Wekelijkse groei followers", "Gem. Reach per post"],
    "Jouw school": [round(total_engagement, 1), 120, round(avg_reach_per_post)],
    "Gemiddelde school": [2.8, 80, 3200]
}
bench_df = pd.DataFrame(benchmark_data)
fig_bench = px.bar(bench_df, x="Metric", y=["Jouw school", "Gemiddelde school"], barmode="group",
                   title="Benchmark vergelijking (mock)")
st.plotly_chart(fig_bench, use_container_width=True)

# ====== Top posts tabel ======
st.subheader("Top Posts (voorbeeld)")
top_posts = pd.DataFrame({
    "Post": ["Open Dag flyer", "Leerling succesverhaal", "Sportdag video", "Kerstgroet", "Nieuwe inschrijvingen"],
    "Datum": ["2025-12-10", "2025-12-05", "2025-11-28", "2025-11-20", "2025-11-15"],
    "Likes": [450, 380, 620, 290, 510],
    "Comments": [45, 32, 78, 21, 56],
    "Reach": [8500, 7200, 12000, 5400, 9800]
})
st.dataframe(top_posts.style.highlight_max(axis=0), use_container_width=True)

# ====== Export ======
st.subheader("📥 Exporteer je rapport")
csv = df.to_csv(index=False).encode()
st.download_button("Download data als CSV", csv, "social_data.csv", "text/csv")

best_platform_safe = df.groupby('Platform')['Engagement Rate (%)'].mean().idxmax() if not df.empty else "Onbekend"
rapport = f"""
# Social Media Rapport - {school_naam}
Periode: {periode[0]} t/m {periode[1]}

Totale followers: {int(total_followers):,}
Gemiddelde engagement: {total_engagement:.1f}%
Beste platform: {best_platform_safe}

Gegenereerd op {datetime.today().strftime('%d-%m-%Y')}
"""
st.download_button("Download rapport als tekst", rapport, "rapport.txt", "text/plain")

st.markdown("---")
st.caption("MVP gebouwd met ❤️ door jou & Grok – Nu crash-vrij en klaar voor de volgende stap!")
