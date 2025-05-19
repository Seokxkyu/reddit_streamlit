# streamlit_app.py
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="🔴 YouTube Music Weekly Analysis", layout="wide")
st.title("🔴 YouTube Music Weekly Analysis")

@st.cache_data
def load_data(path):
    df = pd.read_csv(
        path,
        usecols=['date', 'Artist Name', 'Views'],
        parse_dates=['date']
    )
    df.rename(columns={'Artist Name': 'artist', 'Views': 'views'}, inplace=True)
    return df

df = load_data("data/us_weekly_yt.csv")
pivot_df = df.pivot_table(index='date', columns='artist', values='views', aggfunc='sum')

artist_totals = pivot_df.sum()
sorted_options = sorted(artist_totals.index.tolist(), key=lambda x: artist_totals[x], reverse=True)

default_selection = [artist for artist in ["BTS", "Lady Gaga", "Bruno Mars"] if artist in artist_totals.index]

selected_options = st.multiselect("아티스트 선택", options=sorted_options, default=default_selection)

if selected_options:
    chart_data = pivot_df[selected_options]
    chart_data_reset = chart_data.reset_index().melt("date", var_name="artist", value_name="views")
    
    line_chart = alt.Chart(chart_data_reset).mark_line(strokeWidth=4).encode(
        x=alt.X('date:T', title='Date'),
        y=alt.Y('views:Q', title='Views'),
        color=alt.Color('artist:N', scale=alt.Scale(scheme='dark2'), title='Artist'),
        tooltip=['artist', 'date', 'views']
    ).properties(
        width=800,
        height=500
    )
    st.altair_chart(line_chart, use_container_width=True)
else:
    st.warning("아티스트를 선택하세요.")
