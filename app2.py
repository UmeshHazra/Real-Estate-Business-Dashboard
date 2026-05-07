import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------- PAGE CONFIG --------------------
st.set_page_config(layout="wide")

# -------------------- CUSTOM CSS --------------------
st.markdown("""
<style>

/* 🔹 Apply Times New Roman globally */
html, body, [class*="css"] {
    font-family: "Times New Roman", Times, serif !important;
}

/* 🔹 Background (lighter & elegant) */
body {
    background-color: #F5F5F5;
}

/* 🔹 Main container */
.block-container {
    padding-top: 1rem;
    padding-bottom: 0rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* 🔹 Title styling */
h1 {
    color: #1A1A1A;
    text-align: center;
    font-size: 36px;
    font-weight: bold;
}

/* 🔹 Sidebar */
section[data-testid="stSidebar"] {
    background-color: #EAEAEA;
    font-family: "Times New Roman", Times, serif;
}

/* 🔹 KPI Cards (clean white cards) */
div[data-testid="metric-container"] {
    background-color: white;
    border: 1px solid #D1D5DB;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    color: #111827;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.05);
}

/* 🔹 Chart containers */
div[data-testid="stPlotlyChart"] {
    background-color: white;
    padding: 10px;
    border-radius: 10px;
    border: 1px solid #E5E7EB;
}

/* 🔹 Remove Streamlit header */
header {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# -------------------- TITLE --------------------
st.title("📊 Real Estate Business Dashboard")

# -------------------- LOAD DATA --------------------

url = "https://drive.google.com/uc?id=1V4WvlKKwf4coKJeYJLlyLYVpaZbvudtX"

df = pd.read_csv(url)  # 🔁 change file name
df.columns = df.columns.str.strip()

# -------------------- CITY COORDINATES --------------------
city_coords = {
    "Mumbai": [19.0760, 72.8777],
    "Delhi": [28.7041, 77.1025],
    "Bangalore": [12.9716, 77.5946],
    "Hyderabad": [17.3850, 78.4867],
    "Chennai": [13.0827, 80.2707],
    "Kolkata": [22.5726, 88.3639],
    "Pune": [18.5204, 73.8567],
    "Ahmedabad": [23.0225, 72.5714]
}

# -------------------- SIDEBAR FILTERS --------------------
st.sidebar.header("🔍 Filters")

city = st.sidebar.multiselect(
    "City",
    df['City'].unique(),
    default=df['City'].unique()
)

bhk = st.sidebar.multiselect(
    "BHK",
    sorted(df['BHK'].unique()),
    default=sorted(df['BHK'].unique())
)

furnish = st.sidebar.multiselect(
    "Furnished Status",
    df['Furnished_Status'].unique(),
    default=df['Furnished_Status'].unique()
)

# -------------------- FILTER DATA --------------------
filtered_df = df[
    (df['City'].isin(city)) &
    (df['BHK'].isin(bhk)) &
    (df['Furnished_Status'].isin(furnish))
].copy()

# -------------------- ADD MAP COORDS --------------------
filtered_df["lat"] = filtered_df["City"].map(lambda x: city_coords.get(x, [None, None])[0])
filtered_df["lon"] = filtered_df["City"].map(lambda x: city_coords.get(x, [None, None])[1])

map_df = filtered_df.dropna(subset=["lat", "lon"])

# -------------------- KPI CARDS --------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🏘 Total Listings", filtered_df.shape[0])

with col2:
    st.metric("🏙 Cities", filtered_df['City'].nunique())

with col3:
    st.metric("💰 Avg Price", f"{filtered_df['Price_in_Lakhs'].mean():.2f} Lakhs")

# -------------------- GRAPH GRID --------------------
row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

# -------- PIE CHART --------
with row1_col1:
    type_count = filtered_df['Property_Type'].value_counts().reset_index()
    type_count.columns = ['Property_Type', 'Count']

    fig1 = px.pie(type_count, names='Property_Type', values='Count',
                  title="Property Type Distribution", hole=0.4)
    fig1.update_layout(template="plotly_dark", height=300)
    st.plotly_chart(fig1, use_container_width=True)

# -------- BAR CHART --------
with row1_col2:
    bhk_count = filtered_df['BHK'].value_counts().sort_index().reset_index()
    bhk_count.columns = ['BHK', 'Count']

    fig2 = px.bar(bhk_count, x='BHK', y='Count', text='Count',
                  title="BHK Distribution")
    fig2.update_layout(template="plotly_dark", height=300)
    st.plotly_chart(fig2, use_container_width=True)

# -------- LINE CHART --------
with row2_col1:
    bhk_price = filtered_df.groupby('BHK', as_index=False)['Price_in_Lakhs'].mean()

    fig3 = px.line(bhk_price, x='BHK', y='Price_in_Lakhs',
                   markers=True, title="Avg Price Trend by BHK")
    fig3.update_layout(template="plotly_dark", height=300)
    st.plotly_chart(fig3, use_container_width=True)

# -------- DONUT CHART --------
with row2_col2:
    furnish_count = filtered_df['Furnished_Status'].value_counts().reset_index()
    furnish_count.columns = ['Furnished_Status', 'Count']

    fig4 = px.pie(furnish_count, names='Furnished_Status', values='Count',
                  hole=0.5, title="Furnishing Distribution")
    fig4.update_layout(template="plotly_dark", height=300)
    st.plotly_chart(fig4, use_container_width=True)

# -------- MAP --------
fig_map = px.scatter_mapbox(
    map_df,
    lat="lat",
    lon="lon",
    color="Price_in_Lakhs",
    size="Price_in_Lakhs",
    hover_name="City",
    hover_data=["BHK", "Property_Type"],
    title="📍 Property Prices by Location",
    zoom=4,
    height=300
)

fig_map.update_layout(
    mapbox_style="open-street-map",
    template="plotly_dark"
)

st.plotly_chart(fig_map, use_container_width=True)