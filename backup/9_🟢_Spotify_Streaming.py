import streamlit as st
import pandas as pd
import os
import altair as alt

st.set_page_config(page_title="🟢 Spotify Streaming Analysis", layout="wide")
st.title("🟢 Spotify Streaming Analysis")

@st.cache_data
def load_data():
    csv_path = os.path.join("data", "us_daily_stream.csv")
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df['artist_names'] = df['artist_names'].str.split(',')
    df['artist_names'] = df['artist_names'].apply(lambda lst: [artist.strip() for artist in lst])
    df_exploded = df.explode('artist_names').rename(columns={'artist_names': 'artist'})
    artist_daily = df_exploded.groupby(['date', 'artist'])['streams'].sum().reset_index()
    pivot_df = artist_daily.pivot(index='date', columns='artist', values='streams')
    return pivot_df

pivot_df = load_data()

groups = {
    "BTS": ['BTS', 'Jimin', 'Jung Kook', 'j-hope', 'RM', 'Jin'],
    "BLACKPINK": ['BLACKPINK', 'JENNIE', 'LISA', 'ROSÉ']
}

available_groups = []
for group_name, members in groups.items():
    if any(member in pivot_df.columns for member in members):
        available_groups.append(group_name)

group_members = set()
for members in groups.values():
    group_members.update(members)
individual_artists = [artist for artist in pivot_df.columns if artist not in group_members]

selectable_options = available_groups + individual_artists
artist_totals = pivot_df.sum()
group_totals = {}
for group_name, members in groups.items():
    total = sum(artist_totals[member] for member in members if member in artist_totals)
    group_totals[group_name] = total

option_totals = {}
for group_name in available_groups:
    if group_name in group_totals:
        option_totals[group_name] = group_totals[group_name]
for artist in individual_artists:
    if artist in artist_totals:
        option_totals[artist] = artist_totals[artist]

sorted_options = sorted(option_totals, key=option_totals.get, reverse=True)
default_selection = []
if "BTS" in available_groups:
    default_selection.append("BTS")
if "Bruno Mars" in individual_artists:
    default_selection.append("Bruno Mars")
if "Lady Gaga" in individual_artists:
    default_selection.append("Lady Gaga")

selected_options = st.multiselect(
    "아티스트 선택",
    options=sorted_options,
    default=[opt for opt in sorted_options if opt in default_selection]
)

chart_data = pd.DataFrame(index=pivot_df.index)
for option in selected_options:
    if option in groups:
        members = groups[option]
        series_list = [pivot_df[member] for member in members if member in pivot_df.columns]
        if series_list:
            group_total = series_list[0]
            for s in series_list[1:]:
                group_total = group_total.add(s, fill_value=0)
            chart_data[option] = group_total
        else:
            st.error(f"{option} 그룹에 해당하는 데이터가 존재하지 않습니다.")
    else:
        if option in pivot_df.columns:
            chart_data[option] = pivot_df[option]
        else:
            st.error(f"{option} 데이터가 존재하지 않습니다.")

# options=['tableau10', 'category10', 'accent', 'dark2', 'set1', 'set2'],

if not chart_data.empty:
    chart_data_reset = chart_data.reset_index().melt("date", var_name="artist", value_name="streams")
    line_chart = alt.Chart(chart_data_reset).mark_line(strokeWidth=4).encode(
        x=alt.X('date:T', title='Date'),
        y=alt.Y('streams:Q', title='Streams'),
        color=alt.Color('artist:N', scale=alt.Scale(scheme='dark2'), title='Artist')
    ).properties(
        width=800,
        height=500
    )
    st.altair_chart(line_chart, use_container_width=True)
else:
    st.write("시각화를 위한 데이터가 없습니다.")