import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Google Trends",
    layout="wide"
)
st.title("🌐 Google Trends Analysis")

@st.cache_data
def load_data():
    csv_path = os.path.join("data", "vtuber_5.csv")
    df = pd.read_csv(csv_path, encoding="utf-8", skiprows=1)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={
        "주": "date",
        "にじさんじ: (일본)": "にじさんじ (Nijisanji)",
        "バーチャル: (일본)": "バーチャル (Virtual)",
        "ホロライブ: (일본)": "ホロライブ (HoloLive)",
        "vtuber: (일본)": "vtuber"
    })
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    df = df.sort_values("date").set_index("date")
    df = df.apply(pd.to_numeric, errors="coerce").fillna(0)
    return df

df = load_data()

all_categories = df.columns.tolist()
selected = st.multiselect(
    "키워드 선택",
    options=all_categories,
    default=all_categories
)

min_date = df.index.min().date()
max_date = df.index.max().date()
start_date = st.date_input(
    "시작 날짜",
    value=pd.to_datetime("2020-04-19").date(),
    min_value=min_date,
    max_value=max_date
)
end_date = st.date_input(
    "종료 날짜",
    value=max_date,
    min_value=min_date,
    max_value=max_date
)

if start_date > end_date:
    st.error("시작 날짜가 종료 날짜보다 이전이어야 합니다.")

filtered_df = df.loc[start_date:end_date, selected]

st.subheader("📈 VTuber 키워드 검색량 추이")
st.line_chart(filtered_df)

# 추가: vtuber20 데이터의 line plot (2018-01-01 이후, 필터링 없음)
@st.cache_data
def load_data_vtuber20():
    csv_path = os.path.join("data", "vtuber_20.csv")
    df20 = pd.read_csv(csv_path, encoding="utf-8", skiprows=1)
    df20.columns = df20.columns.str.strip()
    df20 = df20.rename(columns={
        "월": "date",
        "にじさんじ: (일본)": "Nijisanji",
        "バーチャル: (일본)": "Virtual",
        "ホロライブ: (일본)": "HoloLive",
        "vtuber: (일본)": "Vtuber"
    })
    df20.drop(columns=["HoloLive", "Virtual"], inplace=True, errors="ignore")
    df20["date"] = pd.to_datetime(df20["date"], format="%Y-%m")
    df20 = df20.sort_values("date").set_index("date")
    df20 = df20.apply(pd.to_numeric, errors="coerce").fillna(0)
    df20 = df20.loc[pd.to_datetime("2017-01-01"):]
    return df20

st.subheader("📈 버추얼 유튜버 트렌딩 추이 (2017년~)")
df_vt20 = load_data_vtuber20()
import altair as alt
df20_long = df_vt20.reset_index().melt(id_vars="date", var_name="trend", value_name="value")
chart20 = alt.Chart(df20_long).mark_line(point=False).encode(
    x=alt.X("date:T", title="Date"),
    y=alt.Y("value:Q", title="Search"),
    color=alt.Color("trend:N", title="Trend")
).properties(width=700, height=400)
st.altair_chart(chart20)