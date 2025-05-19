import streamlit as st
import pandas as pd
import altair as alt
import os

st.set_page_config(page_title="🎧 Music Streaming Analysis", layout="wide")
st.title("🎧 Music Streaming Analysis")

tab1, tab2 = st.tabs(["🟢 Spotify", "🔴 YouTube Music"])

# ---------- Tab1: Spotify Streaming Analysis ----------
with tab1:
    st.info("[스포티파이 일간 스트리밍 분석](https://charts.spotify.com/charts/view/regional-us-daily/latest)")

    @st.cache_data
    def load_spotify_data():
        csv_path = os.path.join("data", "us_daily_stream.csv")
        df = pd.read_csv(csv_path)
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df['artist_names'] = df['artist_names'].str.split(',')
        df['artist_names'] = df['artist_names'].apply(lambda lst: [artist.strip() for artist in lst])
        df_exploded = df.explode('artist_names').rename(columns={'artist_names': 'artist'})
        artist_daily = df_exploded.groupby(['date', 'artist'])['streams'].sum().reset_index()
        pivot_df = artist_daily.pivot(index='date', columns='artist', values='streams')
        return pivot_df

    spotify_df = load_spotify_data()
    min_date = spotify_df.index.min()
    max_date = spotify_df.index.max()
    start_date, end_date = st.date_input("날짜 선택", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    filtered_spotify_df = spotify_df.loc[start_date:end_date]
    
    groups = {
        "BTS": ['BTS', 'Jimin', 'Jung Kook', 'j-hope', 'RM', 'Jin'],
        "BLACKPINK": ['BLACKPINK', 'JENNIE', 'LISA', 'ROSÉ']
    }
    available_groups = []
    for group_name, members in groups.items():
        if any(member in filtered_spotify_df.columns for member in members):
            available_groups.append(group_name)
    individual_artists = list(filtered_spotify_df.columns)  # now include all artists, even group members

    artist_totals = filtered_spotify_df.sum()
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

    default_selection = ['BTS', 'Bruno Mars', 'Lady Gaga']

    selected_options_spotify = st.multiselect(
        "아티스트 선택",
        options=sorted_options,
        default=[opt for opt in sorted_options if opt in default_selection]
    )

    chart_data_spotify = pd.DataFrame(index=filtered_spotify_df.index)
    for option in selected_options_spotify:
        if option in groups:
            members = groups[option]
            series_list = [filtered_spotify_df[member] for member in members if member in filtered_spotify_df.columns]
            if series_list:
                group_total = series_list[0]
                for s in series_list[1:]:
                    group_total = group_total.add(s, fill_value=0)
                chart_data_spotify[option] = group_total
            else:
                st.error(f"{option} 그룹에 해당하는 데이터가 존재하지 않습니다.")
        else:
            if option in filtered_spotify_df.columns:
                chart_data_spotify[option] = filtered_spotify_df[option]
            else:
                st.error(f"{option} 데이터가 존재하지 않습니다.")

    if not chart_data_spotify.empty:
        chart_data_reset = chart_data_spotify.reset_index().melt("date", var_name="artist", value_name="streams")
        line_chart = alt.Chart(chart_data_reset).mark_line(strokeWidth=4).encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('streams:Q', title='Streams'),
            color=alt.Color('artist:N', scale=alt.Scale(scheme='dark2'), title='Artist'),
            tooltip=['artist', 'date', 'streams']
        ).properties(
            width=800,
            height=500
        )
        st.altair_chart(line_chart, use_container_width=True)
    else:
        st.write("시각화를 위한 데이터가 없습니다.")

# ---------- Tab2: YouTube Music Weekly Views ----------
with tab2:
    st.info("[유튜브 뮤직 주간 스트리밍 분석](https://charts.youtube.com/charts/TopArtists/us/weekly)") 

    @st.cache_data
    def load_yt_data():
        csv_path = os.path.join("data", "us_weekly_yt.csv")
        df = pd.read_csv(
            csv_path,
            usecols=['date', 'Artist Name', 'Views'],
            parse_dates=['date']
        )
        df.rename(columns={'Artist Name': 'artist', 'Views': 'views'}, inplace=True)
        return df

    yt_df = load_yt_data()
    pivot_yt = yt_df.pivot_table(index='date', columns='artist', values='views', aggfunc='sum')
    # Add date input and filter the pivot table using its min and max dates
    min_date_yt = pivot_yt.index.min()
    max_date_yt = pivot_yt.index.max()
    start_date_yt, end_date_yt = st.date_input("날짜 선택", value=(min_date_yt, max_date_yt), min_value=min_date_yt, max_value=max_date_yt)
    filtered_pivot_yt = pivot_yt.loc[start_date_yt:end_date_yt]
    
    groups = {
        "BTS": ['BTS', 'Jimin', 'Jung Kook', 'j-hope', 'RM', 'Jin'],
        "BLACKPINK": ['BLACKPINK', 'JENNIE', 'LISA', 'ROSÉ']
    }
    available_groups_yt = []
    for group_name, members in groups.items():
        if any(member in filtered_pivot_yt.columns for member in members):
            available_groups_yt.append(group_name)
    individual_artists_yt = list(filtered_pivot_yt.columns)  
    
    artist_totals_yt = filtered_pivot_yt.sum()
    option_totals_yt = {}
    for group_name in available_groups_yt:
        total = sum(artist_totals_yt[member] for member in groups[group_name] if member in artist_totals_yt)
        option_totals_yt[group_name] = total
    for artist in individual_artists_yt:
        if artist in artist_totals_yt:
            option_totals_yt[artist] = artist_totals_yt[artist]
    sorted_options_yt = sorted(option_totals_yt, key=option_totals_yt.get, reverse=True)
    
    default_selection_yt = ["BTS", "Bruno Mars", "Lady Gaga"]
    selected_options_yt = st.multiselect("아티스트 선택", options=sorted_options_yt, default=default_selection_yt)
    
    if selected_options_yt:
        chart_data_yt = pd.DataFrame(index=filtered_pivot_yt.index)
        for option in selected_options_yt:
            if option in groups:
                members = groups[option]
                series_list = [filtered_pivot_yt[member] for member in members if member in filtered_pivot_yt.columns]
                if series_list:
                    group_total = series_list[0]
                    for s in series_list[1:]:
                        group_total = group_total.add(s, fill_value=0)
                    chart_data_yt[option] = group_total
                else:
                    st.error(f"{option} 그룹에 해당하는 데이터가 존재하지 않습니다.")
            else:
                if option in filtered_pivot_yt.columns:
                    chart_data_yt[option] = filtered_pivot_yt[option]
                else:
                    st.error(f"{option} 데이터가 존재하지 않습니다.")
    
        chart_data_reset_yt = chart_data_yt.reset_index().melt("date", var_name="artist", value_name="views")
        line_chart_yt = alt.Chart(chart_data_reset_yt).mark_line(strokeWidth=4).encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('views:Q', title='Views'),
            color=alt.Color('artist:N', scale=alt.Scale(scheme='dark2'), title='Artist'),
            tooltip=['artist', 'date', 'views']
        ).properties(
            width=800,
            height=500
        )
        st.altair_chart(line_chart_yt, use_container_width=True)
    else:
        st.warning("아티스트를 선택하세요.")