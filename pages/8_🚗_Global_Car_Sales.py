import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="🚗 Global Car Sales", layout="wide")
st.title("Global Car Sales")

@st.cache_data
def load_region_data(region: str, path: str) -> pd.DataFrame:
    df = pd.read_excel(path, engine="openpyxl")
    cols = df.columns.tolist()
    
    if region == "US":
        df = df.rename(columns={cols[0]: "Automaker", cols[1]: "Brand"})
    else:
        df = df.rename(columns={cols[0]: "Brand"})
    
    df = df.set_index("Brand")
    if "Automaker" in df.columns:
        df = df.drop(columns=["Automaker"])
    
    df.columns = pd.to_datetime(df.columns)
    df = df.sort_index(axis=1)
    return df

DATA_FILES = {
    "US": "data/us_sales_2019_2025.xlsx",
    "Europe": "data/europe_sales_2020_2025.xlsx",
    "China": "data/china_sales_2020_2025.xlsx",
}

tabs = st.tabs(list(DATA_FILES.keys()))
for region, tab in zip(DATA_FILES.keys(), tabs):
    with tab:
        df = load_region_data(region, DATA_FILES[region])

        # --- compute top 10 by Mar 2025 once ---
        target = pd.to_datetime("2025-03-01")
        if target not in df.columns:
            st.error("❌ 2025-03-01 데이터가 없습니다.")
            continue
        top10 = df[target].sort_values(ascending=False).head(9).index.tolist()

        # --- pick defaults according to region ---
        if region == "Europe":
            automaker_list = [
                "Volkswagen Group","Stellantis","Renault Group","Hyundai Group",
                "Toyota Group","BMW Group","Mercedes-Benz","Ford","Volvo Cars",
                "Tesla","Nissan","SAIC Motor","Suzuki","Mazda",
                "Jaguar Land Rover Group","Honda","Mitsubishi"
            ]
            brand_list = [
                "Volkswagen","Skoda","Audi","Seat","Cupra","Porsche",
                "Peugeot","Opel/Vauxhall","Citroen","Fiat","Jeep","DS",
                "Lancia/Chrysler","Alfa Romeo","Renault","Dacia","Alpine",
                "Kia","Hyundai","Toyota","Lexus","BMW","Mini","Mercedes",
                "Smart","Ford","Volvo Cars","Tesla","Nissan","SAIC Motor",
                "Suzuki","Mazda","Land Rover","Jaguar","Honda","Mitsubishi"
            ]
            auto_opts  = [a for a in automaker_list if a in df.index]
            brand_opts = [b for b in brand_list     if b in df.index]

            view = st.radio(
                "View mode",
                ["Automaker", "Brand"],
                horizontal=True,
                key=f"view_{region}"
            )

            if view == "Automaker":
                default_auto = [a for a in top10 if a in auto_opts]
                sel = st.multiselect(
                    "제조사 선택",
                    options=auto_opts,
                    default=default_auto,
                    key=f"multi_auto_{region}"
                )
            else:
                default_brand = [b for b in top10 if b in brand_opts]
                sel = st.multiselect(
                    "브랜드 선택",
                    options=brand_opts,
                    default=default_brand,
                    key=f"multi_brand_{region}"
                )

        else:
            brands = df.index.tolist()
            default_br = [b for b in top10 if b in brands]
            sel = st.multiselect(
                "브랜드 선택",
                options=brands,
                default=default_br,
                key=f"multi_{region}"
            )

        if not sel:
            st.warning("최소 하나를 선택해주세요.")
            continue

        # --- build and plot ---
        plot_df = (
            df.loc[sel]
              .T
              .reset_index()
              .melt(id_vars="index", var_name="Brand", value_name="Sales")
              .rename(columns={"index": "Date"})
        )

        chart = (
            alt.Chart(plot_df)
                .mark_line(point=True)
                .encode(
                    x=alt.X("Date:T", title="Date"),
                    y=alt.Y("Sales:Q", title="Monthly Sales"),
                    color=alt.Color("Brand:N", legend=alt.Legend(title="Brand")),
                    tooltip=["Brand:N", "Date:T", "Sales:Q"],
                )
                .properties(
                    height=600,
                    title=f"{region} Monthly Sales"
                )
                .interactive()
        )
        st.altair_chart(chart, use_container_width=True)