
import folium
import pandas as pd
import streamlit as st 
from streamlit_folium import st_folium
from utils.dataloader import TransformedData
from utils.processes import DashboardProcesses

# Allow the Streamlit app to use the full browser width so maps can expand

data = TransformedData()
processes = DashboardProcesses()


def load_data():
    listings_with_ratings = data.transform_listings_with_ratings()
    neighbourhoods = data.transform_neighbourhoods()
    hosts = data.transform_hosts()

    return listings_with_ratings, neighbourhoods, hosts


def get_ward_options(neighbourhoods):
    sorted_wards = processes.sort_wards(neighbourhoods, 'name')
    return sorted_wards


def run_listings_processes(option, listings_with_ratings):
    # Filter listings by selected ward
    listings_info = processes.filter_listings_by_ward(listings_with_ratings, option)
    listing_metrics = processes.get_metrics_for_ward_listings(listings_info)
    data_table = processes.get_data_table(listings_with_ratings)
    ward_hosts = listings_info['host_id'].unique()

    return listings_info, listing_metrics, data_table, ward_hosts


def run_neighbourhood_processes(option, neighbourhoods):
    neighbourhood_info = processes.filter_ward_by_option(neighbourhoods, option)
    
    return neighbourhood_info


def run_host_processes(option, hosts, ward_hosts):
    host_info = processes.filter_hosts_by_ward(hosts, ward_hosts, option)
    host_metrics = processes.get_metrics_for_ward_hosts(host_info)

    return host_metrics

listings_with_ratings, neighbourhoods, hosts = load_data()


st.set_page_config(layout="wide")
st.sidebar.title("Airbnb Listing Price Dashboard")  

# Neighbourhood selection dropdown
option = st.sidebar.selectbox(
    "Select Ward", 
    index = None,
    placeholder="Select a ward",
    options=get_ward_options(neighbourhoods),
    key='ward_select'
)

listings_info, listing_metrics, data_table, ward_hosts \
= run_listings_processes(option, listings_with_ratings)
neighbourhood_info = run_neighbourhood_processes(option, neighbourhoods)
host_metrics = run_host_processes(option, hosts, ward_hosts)

if not option:
    latitude = -34.0
    longitude = 18.5
    zoom = 10
else:
    latitude = neighbourhood_info['latitude'].values[0]
    longitude = neighbourhood_info['longitude'].values[0]
    zoom = 12

st.sidebar.divider()
st.sidebar.markdown("### Selected Ward Information")
st.sidebar.markdown(f"Current Selection: :blue-background[:green[{option}]]")
st.sidebar.markdown(f"Longitude: :blue-background[:blue[{longitude:.5f}]]")
st.sidebar.markdown(f"Latitude: :blue-background[:blue[{latitude:.5f}]]")
st.sidebar.markdown(f"Total Hosts: :blue-background[:blue[{listing_metrics['total_hosts']}]]")
st.sidebar.markdown(f"Total Listings: :blue-background[:blue[{listing_metrics['total_listings']}]]")
st.sidebar.markdown(f"Average Rating: :blue-background[:yellow[{listing_metrics['average_rating']: .2f} stars]]")
st.sidebar.markdown(f"Average Price: :blue-background[:blue[ZAR {listing_metrics['average_price']: .2f} per night]]")
st.sidebar.divider()
st.sidebar.markdown("### About this Dashboard")
st.sidebar.markdown("This is a dashboard that displays Airbnb listings in Cape Town, South Africa. The data is sourced from [Inside Airbnb](http://insideairbnb.com/get-the-data.html) and is updated monthly.")    

st.markdown("## Airbnb Listings in Cape Town by Ward")

    
col1, col2, col3, col4 = st.columns(4)
col1.metric("Min Price", f"ZAR {listing_metrics['min_price']:.2f}")
col2.metric("Max Price", f"ZAR {listing_metrics['max_price']:.2f}")
col3.metric("Min Rating", f"{listing_metrics['min_rating']:.2f} star(s)")
col4.metric("Max Rating", f"{listing_metrics['max_rating']:.2f} star(s)")
col1.metric("Avg. Host Response Rate", f"{host_metrics['mean_response_rate']:.2f}%")
col2.metric("Avg. Host Acceptance Rate", f"{host_metrics['mean_acceptance_rate']:.2f}%")
col3.metric("Superhosts (%)", f"{host_metrics['super_hosts_count']:.2f}%")
col4.metric("Verified Hosts (%)", f"{host_metrics['verified_hosts_count']:.2f}%")

with st.container():
    col1, col2 = st.columns([3, 2], vertical_alignment="center")
    n=folium.Map(location=[latitude, longitude], zoom_start=zoom)
    if option:
        for _, row in listings_info.iterrows():
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=(
                        f"Price: ZAR {row['price_usd']:.2f} per night<br>"
                        f"Rating: {row['review_scores_rating']:.1f} stars"
                ),
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(n)
    with col1:
    
        st_data = st_folium(n, width="stretch", height=400)  
        

    with col2:
        st.markdown("### Listings Data Table")
        st.dataframe(data_table, width='stretch')