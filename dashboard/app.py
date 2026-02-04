
import folium
import pandas as pd
import streamlit as st 
from streamlit_folium import st_folium
from utils.helpers import NeighbourhoodsHelper, ListingsHelper, HostsHelper

# Allow the Streamlit app to use the full browser width so maps can expand

neighbourhoods_helper = NeighbourhoodsHelper()
ward_options = neighbourhoods_helper.get_ward_options()


st.set_page_config(layout="wide")
st.sidebar.title("Airbnb Listing Price Dashboard")  

# Neighbourhood selection dropdown
option = st.sidebar.selectbox(
    "Select Ward", 
    index = None,
    placeholder="Select a ward",
    options=ward_options,
    key='ward_select'
)

if not option:
    latitude = -34.0
    longitude = 18.5
    zoom = 10
else:
    filtered_neighbourhoods = neighbourhoods_helper.get_filtered_neighbourhood(option)
    latitude = filtered_neighbourhoods['latitude'].values[0]
    longitude = filtered_neighbourhoods['longitude'].values[0]
    zoom = 12

listings_helper = ListingsHelper(option)
filtered_listings = listings_helper.get_filtered_listings()
listing_metrics = listings_helper.get_listing_metrics()
listing_deltas = listings_helper.get_listing_metrics_deltas()

hosts_helper = HostsHelper(option, filtered_listings)
host_metrics = hosts_helper.get_filtered_host_metrics()
global_host_metrics = hosts_helper.get_global_host_metrics() 
host_deltas = hosts_helper.get_host_metrics_deltas()

st.sidebar.divider()
if option:
    st.sidebar.markdown(f"### Ward {option} Summary")
else:
    st.sidebar.markdown("### Cape Town Summary")
st.sidebar.markdown(f"Longitude: :blue-background[:blue[{longitude:.5f}]]")
st.sidebar.markdown(f"Latitude: :blue-background[:blue[{latitude:.5f}]]")
st.sidebar.markdown(f"Total Hosts: :blue-background[:blue[{listing_metrics['total_hosts']}]]")
st.sidebar.markdown(f"Total Listings: :blue-background[:blue[{listing_metrics['total_listings']}]]")
st.sidebar.markdown(f"Lowest Rating: :blue-background[:red[{listing_metrics['min_rating']: .2f} stars]]")
st.sidebar.markdown(f"Highest Rating: :blue-background[:green[{listing_metrics['max_rating']: .2f} stars]]")
st.sidebar.markdown(f"Average Price: :blue-background[:yellow[ZAR {listing_metrics['average_price']: .2f} per night]]")
st.space(size="small")
st.sidebar.divider()
st.sidebar.markdown("### About this Dashboard")
st.sidebar.markdown("This is a dashboard that displays Airbnb listings in Cape Town, South Africa. The data is sourced from [Inside Airbnb](http://insideairbnb.com/get-the-data.html) and is updated monthly.")    

st.markdown("## Airbnb Listings in Cape Town by Ward")
st.markdown("### Overall Metrics")

with st.expander("Listings Metrics", expanded=False):
    st.markdown(
        """
        Key Airbnb metrics for selected ward vs Cape Town overall:
        - **Lowest/Highest Price** in ward
        - **Avg Price** (with Cape Town difference)  
        - **Avg Rating** (with Cape Town difference)
        """
    )
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Lowest Price", 
        f"ZAR {listing_metrics['min_price']:.2f}"
    )
    col2.metric(
        "Highest Price", 
        f"ZAR {listing_metrics['max_price']:.2f}",
    )
    col3.metric(
        "Average Price", 
        f"ZAR {listing_metrics['average_price']:.2f}",
        f"{listing_deltas['average_price_delta']:.2f} ZAR")
    col4.metric(
        "Average Rating", f"{
        listing_metrics['average_rating']:.2f} star(s)",
        f"{listing_deltas['average_rating_delta']:.1f} star(s)" 
        )
   

# Display host metrics
with st.expander("Host Metrics", expanded=False):
    st.markdown(
        """
        Key Airbnb host metrics for selected ward vs Cape Town overall:
        - **Avg. Host Response Rate** (with Cape Town difference)
        - **Avg. Host Acceptance Rate** (with Cape Town difference)  
        - **Verified Hosts (%)** (with Cape Town difference)
        - **Superhosts (%)** (with Cape Town difference)
        """
    )   
    st.markdown("### Host Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Avg. Host Response Rate", 
        f"{host_metrics['mean_response_rate']:.2f}%",
        f"{host_deltas['mean_response_rate_delta']:.2f}%")
    col2.metric(
        "Avg. Host Acceptance Rate", 
        f"{host_metrics['mean_acceptance_rate']:.2f}%",
        f"{host_deltas['mean_acceptance_rate_delta']:.2f}%")
    col3.metric(
        "Verified Hosts (%)", 
        f"{host_metrics['verified_hosts_percent']:.2f}%",
        f"{host_deltas['verified_hosts_percent_delta']:.2f}%")
    col4.metric(
        "Superhosts (%)", 
        f"{host_metrics['super_hosts_percent']:.2f}%",
        f"{host_deltas['super_hosts_percent_delta']:.2f}%"
    )

st.divider()
with st.container():
    col1, col2 = st.columns([45, 55], vertical_alignment="center")
    n=folium.Map(location=[latitude, longitude], zoom_start=zoom)
    if option:
        for _, row in filtered_listings.iterrows():
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=(
                        f"Price: ZAR {row['price_usd']:.2f} per night<br>"
                        f"Rating: {row['review_scores_rating']:.1f} stars"
                ),
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(n)

    with col1:
        data_table = listings_helper.get_data_table()
        st.markdown("### Listings Data Table")
        st.dataframe(data_table, width='stretch')
   
    with col2:
        st.markdown("### Listings Map")
        st_data = st_folium(n, width="stretch", height=400)  