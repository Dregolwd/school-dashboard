import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm

# Pagina configuratie
st.set_page_config(page_title="SchoolSocial Dashboard", page_icon="🏫", layout="wide")

# ====== Sidebar: School personalisatie & filters ======
st.sidebar.header("School instellingen")
school_naam = st.sidebar.text_input("Schoolnaam", value="Jouw Basisschool")
school_logo = st.sidebar.text_input("Logo URL (optioneel)", value="https://via.placeholder.com/150?text=🏫")

if school_logo and "placeholder" not in school_logo:
    try:
        st.sidebar.image(school_logo, width=150)
    except:
        pass
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
base_offset = len(school_naam) * 100

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
fig_reach.add_trace(go.Scatter(x=df["Date"], y=df["Reach"], mode='lines+markers', name='Reach'))
fig_reach.add_trace(go.Bar(x=df["Date"], y=df["Likes"], name='Likes'))
st.plotly_chart(fig_reach, use_container_width=True)

st.subheader("🕒 Beste tijd om te posten")
weekday_eng = df.groupby('Weekday')['Engagement Rate (%)'].mean().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], fill_value=0)
best_day = weekday_eng.idxmax()
best_value = weekday_eng.max()

st.write(f"**Beste dag:** {best_day} (gem. {best_value:.1f}% engagement)")
st.info("Tip: Post tussen 15:00 - 17:00 uur voor maximaal bereik bij ouders, of 12:00 - 14:00 voor leerlingen.")

# ====== Engagement trend alert ======
engagement_trend = df["Engagement Rate (%)"].pct_change().mean()
if engagement_trend < -0.05:
    st.error("⚠️ Let op: Engagement daalt de laatste periode. Overweeg meer video-content!")
elif engagement_trend > 0.05:
    st.success("✅ Goed bezig! Engagement stijgt!")

# ====== Top 5 best presterende posts ======
st.subheader("📈 Top 5 best presterende posts")
top_posts = pd.DataFrame({
    "Post": ["Open Dag 2025", "Sportdag video", "Leerling succesverhaal", "Kerstgroet", "Nieuwe inschrijvingen"],
    "Datum": ["10-12-2025", "05-12-2025", "28-11-2025", "20-11-2025", "15-11-2025"],
    "Platform": ["Instagram", "TikTok", "Instagram", "Facebook", "Instagram"],
    "Likes": [620, 890, 510, 420, 580],
    "Comments": [78, 145, 56, 48, 72],
    "Reach": [12000, 18000, 9800, 8500, 11000]
}).sort_values("Reach", ascending=False)

st.dataframe(top_posts.style.highlight_max(axis=0), use_container_width=True)

# ====== Insights & Tips ======
st.subheader("📊 Insights & Tips")
if df['Platform'].nunique() > 1:
    best = df.groupby('Platform')['Engagement Rate (%)'].mean().idxmax()
    st.success(f"**Sterkste platform:** {best} – focus hier meer op!")

tiktok_df = df[df['Platform'] == 'TikTok']
if not tiktok_df.empty and len(tiktok_df) > 1:
    tiktok_growth = tiktok_df['Followers'].iloc[-1] - tiktok_df['Followers'].iloc[0]
    st.info(f"**TikTok groei:** +{int(tiktok_growth)} followers in deze periode!")
else:
    st.info("**TikTok tip:** Kies 'Alle platforms' of 'TikTok' om groeidata te zien.")

st.info("**Algemene tip:** Video's op TikTok scoren het best bij scholen. Post op dinsdag of donderdag!")

# ====== PDF-rapport genereren ======
st.subheader("📄 Genereer PDF-rapport")

if st.button("Maak PDF-rapport"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    # Logo
    if school_logo and "placeholder" not in school_logo:
        try:
            story.append(Image(school_logo, width=3*cm, height=3*cm))
            story.append(Spacer(1, 0.5*cm))
        except:
            pass

    story.append(Paragraph(f"<font size=18><b>Social Media Rapport - {school_naam}</b></font>", styles["Title"]))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"Periode: {periode[0].strftime('%d-%m-%Y')} t/m {periode[1].strftime('%d-%m-%Y')}", styles["Normal"]))
    story.append(Spacer(1, 0.5*cm))

    # Metrics tabel
    data_table = [
        ["Metric", "Waarde"],
        ["Totale Followers", f"{int(total_followers):,}"],
        ["Gem. Engagement Rate", f"{total_engagement:.1f}%"],
        ["Totale Reach", f"{int(total_reach):,}"],
        ["Totale Interacties", f"{int(total_interactions):,}"]
    ]
    table = Table(data_table)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 1*cm))

    # Insights
    story.append(Paragraph("<b>Insights & Tips</b>", styles["Heading2"]))
    if df['Platform'].nunique() > 1:
        best = df.groupby('Platform')['Engagement Rate (%)'].mean().idxmax()
        story.append(Paragraph(f"• Sterkste platform: <b>{best}</b>", styles["Normal"]))
    story.append(Paragraph("• Tip: Video's op TikTok scoren het best bij scholen", styles["Normal"]))
    story.append(Spacer(1, 1*cm))

    story.append(Paragraph(f"Gegenereerd op {datetime.today().strftime('%d-%m-%Y')}", styles["Italic"]))

    doc.build(story)
    buffer.seek(0)

    st.download_button(
        label="📄 Download PDF-rapport",
        data=buffer,
        file_name=f"Social_Rapport_{school_naam.replace(' ', '_')}_{periode[1].strftime('%Y%m%d')}.pdf",
        mime="application/pdf"
    )

# ====== Export CSV ======
st.subheader("📥 Exporteer ruwe data")
csv = df.to_csv(index=False).encode()
st.download_button("Download data als CSV", csv, "social_data.csv", "text/csv")

st.caption("Dashboard uitgebreid met PDF-rapport, top posts, alerts en meer – klaar voor scholen! 🚀")
