import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Google Trending Analysis", layout="wide")
st.title("🌐 Google Trending Analysis")

@st.cache_data
def load_data():
    csv_path = os.path.join("data", "google_trends_hoka.csv")
    df = pd.read_csv(csv_path, parse_dates=["주"], encoding="utf-8", skiprows=1)

    df = df.rename(columns={'주': 'date', 'hoka: (미국)': 'hoka'})

    df = df.sort_values("date")
    return df

df = load_data()

df = df.set_index("date")

st.subheader("📈 Visualization")
st.line_chart(df["hoka"])

st.subheader("📄 Data Preview")
st.dataframe(df)