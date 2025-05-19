import streamlit as st
import pandas as pd
import altair as alt
import os

st.set_page_config(page_title="💿 Album Sales Analysis", layout="wide")
st.title("💿 Album Sales Analysis")

base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(os.path.dirname(base_dir), "data")

@st.cache_data
def load_data():
    csv_path = os.path.join(data_dir, "album_sales.csv")
    df = pd.read_csv(csv_path)
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()
artists = sorted(df["Artist"].unique())

tab1, tab2, tab3 = st.tabs(["아티스트 별 앨범 판매량 추이", "아티스트 간 앨범 판매량 비교", "최근 앨범 판매량 추이"])


with tab1:
    st.info("[써클차트 월간 앨범차트 분석](https://circlechart.kr/page_chart/album.circle)")
    default_artist = "방탄소년단" if "방탄소년단" in artists else artists[0]
    selected_artist = st.selectbox("아티스트 선택", options=artists, index=artists.index(default_artist), key="single_artist")
    
    df_single = df[df["Artist"] == selected_artist]
    grouped_single = df_single.groupby(["Date", "Album"], as_index=False)["Sales"].sum()
    
    chart_single = alt.Chart(grouped_single).mark_bar(size=8).encode(
        x=alt.X("Date:T", title="Date", axis=alt.Axis(labelAngle=0)),
        xOffset=alt.X("Album:N", title="Album"),
        y=alt.Y("Sales:Q", title="Sales"),
        color=alt.Color("Album:N",
                        scale=alt.Scale(scheme="category20"),
                        title="Album"),
        tooltip=["Date", "Album", "Sales"]
    ).properties(width=700, height=500)

    st.altair_chart(chart_single, use_container_width=True)

with tab2:
    default_compare = ["방탄소년단", "세븐틴"] if ("세븐틴" in artists and "방탄소년단" in artists) else artists[:2]
    compare_artists = st.multiselect("비교할 아티스트 선택", options=artists, default=default_compare, key="compare_artists")
    
    if len(compare_artists) < 2:
         st.info("2명 이상의 아티스트를 선택하세요.")
    else:
         df_compare = df[df["Artist"].isin(compare_artists)]
         grouped_compare = df_compare.groupby(["Year_Month", "Artist"], as_index=False)["Sales"].sum()
         
         chart_compare = alt.Chart(grouped_compare).mark_bar(size=10).encode(
             x=alt.X("Year_Month:N", title="Month", axis=alt.Axis(labelAngle=35)),
             xOffset=alt.X("Artist:N", title="Artist"),
             y=alt.Y("Sales:Q", title="Total Sales"),
             color=alt.Color("Artist:N", title="Artist"),
             tooltip=["Year_Month", "Artist", "Sales"]
         ).properties(width=700, height=500)
         
         st.altair_chart(chart_compare, use_container_width=True)


with tab3:
    n_albums = st.number_input("최근 비교 앨범 수 선택", min_value=1, max_value=20, value=3, step=1, key="num_albums")
    default_artists = ["RIIZE", "NCT WISH", "아일릿(ILLIT)", "BOYNEXTDOOR", "izna (이즈나)"]
    # default_artists = ["방탄소년단", "세븐틴"] if "세븐틴" in artists and "방탄소년단" in artists else ["방탄소년단"]    
    filter_artists = st.multiselect("비교할 아티스트 선택", options=artists, default=default_artists, key="compare_artists_tab3")
    
    if not filter_artists:
        st.info("비교할 아티스트를 선택하세요.")
    else:
        df_filtered = df[df["Artist"].isin(filter_artists)].copy()
        df_sorted = df_filtered.sort_values(["Artist", "Date"], ascending=[True, False])
        df_recent = df_sorted.groupby("Artist").head(n_albums).copy()
        df_recent = df_recent.sort_values(["Artist", "Date"], ascending=[True, True])
        df_recent["Album Order"] = df_recent.groupby("Artist")["Sales"].transform(
            lambda s: (s.reset_index(drop=True).index + 1 + (n_albums - len(s)) if len(s) < n_albums else s.reset_index(drop=True).index + 1)
        )
        
        chart = alt.Chart(df_recent).mark_bar(size=20).encode(
            x=alt.X("Album Order:O", title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Sales:Q", title="판매량"),
            color=alt.Color("Album Order:O", title="앨범 순서", scale=alt.Scale(scheme="tableau10")),
            tooltip=["Artist", "Album", "Sales", "Year_Month"],
        ).properties(width=120, height=400).facet(
            column=alt.Column("Artist:N", title="아티스트", header=alt.Header(labelFontWeight='bold'))
        )
        
        st.altair_chart(chart, use_container_width=True)