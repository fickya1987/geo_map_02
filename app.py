# app.py

import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from folium.plugins import AntPath

# Load the data
@st.cache_data
def load_route_data():
    return pd.read_excel("Rute_Perdagangan_Provinsi.xlsx")

@st.cache_data
def load_geojson():
    # Load the Indonesian provinces GeoJSON file
    return gpd.read_file("indonesia.geojson")

# Main App
st.title("Peta Rute Perdagangan Antar Provinsi di Indonesia")

# Load the data
rute_data = load_route_data()
geojson_data = load_geojson()

# Display loaded data
st.write("Data Rute Perdagangan:", rute_data)

# Standardize the 'Provinsi' column in both dataframes for consistency
geojson_data['Provinsi'] = geojson_data['Provinsi'].str.strip().str.upper()
rute_data['Provinsi'] = rute_data['Provinsi'].str.strip().str.upper()

# Merge route data with GeoJSON to add geometry for mapping
merged = geojson_data.merge(rute_data, on='Provinsi', how='inner')

# Map setup
m = folium.Map(location=[-2.5, 118], zoom_start=5, min_zoom=4, max_zoom=7)

# Marker Cluster for all points
marker_cluster = MarkerCluster().add_to(m)
for idx, row in merged.iterrows():
    # Create a popup with trade route details for each province
    popup_info = f"""
    <strong>{row['Provinsi']}</strong><br>
    <strong>Pembelian Terbesar:</strong> {row['Pembelian Terbesar']}<br>
    <strong>Penjualan Terbesar:</strong> {row['Penjualan Terbesar']}
    """
    popup = folium.Popup(popup_info, max_width=300, min_width=200)
    tooltip = folium.Tooltip(row['Provinsi'], sticky=True)
    
    # Marker for each province
    folium.Marker(
        location=[row['geometry'].centroid.y, row['geometry'].centroid.x],
        popup=popup,
        tooltip=tooltip
    ).add_to(marker_cluster)

# Draw routes based on Pembelian Terbesar and Penjualan Terbesar columns
for idx, row in merged.iterrows():
    start_coords = [row['geometry'].centroid.y, row['geometry'].centroid.x]
    
    # Pembelian Terbesar route
    pembelian_prov = row['Pembelian Terbesar'].split(" ")[0].upper()
    pembelian_target = merged[merged['Provinsi'] == pembelian_prov]
    if not pembelian_target.empty:
        pembelian_coords = [pembelian_target['geometry'].centroid.y.values[0], pembelian_target['geometry'].centroid.x.values[0]]
        AntPath(
            locations=[start_coords, pembelian_coords],
            color="green",
            weight=3,
            opacity=0.7,
            dash_array="5, 5"
        ).add_to(m)
    
    # Penjualan Terbesar route
    penjualan_prov = row['Penjualan Terbesar'].split(" ")[0].upper()
    penjualan_target = merged[merged['Provinsi'] == penjualan_prov]
    if not penjualan_target.empty:
        penjualan_coords = [penjualan_target['geometry'].centroid.y.values[0], penjualan_target['geometry'].centroid.x.values[0]]
        AntPath(
            locations=[start_coords, penjualan_coords],
            color="blue",
            weight=3,
            opacity=0.7,
            dash_array="10, 10"
        ).add_to(m)

# Render Map in Streamlit
st.subheader("Peta Provinsi dan Jalur Perdagangan Terbesar")
st_data = st_folium(m, width=700, height=500)
