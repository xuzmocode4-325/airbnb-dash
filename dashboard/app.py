
import folium
import pandas as pd
import streamlit as st 
import streamlit.components.v1 as components
from streamlit_folium import st_folium
from utils.helpers.hosts import HostsHelper
from utils.helpers.listings import ListingsHelper
from utils.helpers.neighbourhoods import NeighbourhoodsHelper

# Allow the Streamlit app to use the full browser width so maps can expand

@st.cache_resource
def get_neighbourhoods_helper():
    return NeighbourhoodsHelper()

@st.cache_data
def get_neighbourhood_data(option):
    """Cache neighbourhood data based on selected ward"""
    neighbourhoods_helper = get_neighbourhoods_helper()
    filtered_neighbourhoods = neighbourhoods_helper.get_filtered_neighbourhood(option)
    hood_metrics = neighbourhoods_helper.get_neighbourhood_sentiment_metrics(option)
    hood_deltas = neighbourhoods_helper.get_neighbourhood_sentiment_deltas(option)
    return filtered_neighbourhoods, hood_metrics, hood_deltas


@st.cache_data
def get_listings_data(option):
    """Cache listings data based on selected ward"""
    listings_helper = ListingsHelper(option)
    filtered_listings = listings_helper.get_filtered_listings()
    listing_metrics = listings_helper.get_listing_metrics()
    listing_deltas = listings_helper.get_listing_deltas()
    return filtered_listings, listing_metrics, listing_deltas

@st.cache_data
def get_host_data(option, filtered_listings):
    """Cache host data based on selected ward"""
    hosts_helper = HostsHelper(option, filtered_listings)
    host_metrics = hosts_helper.get_filtered_host_metrics()
    global_host_metrics = hosts_helper.get_global_host_metrics()
    host_deltas = hosts_helper.get_host_deltas()
    return host_metrics, global_host_metrics, host_deltas


def get_tree_chart(option):
    """Cache sunburst chart for given ward"""
    listings_helper = ListingsHelper(option)
    return listings_helper.show_tree_chart()


def get_wordcloud_svg(option):
    """Cache wordcloud SVG for given ward"""
    neighbourhoods_helper = get_neighbourhoods_helper()
    return neighbourhoods_helper.show_neighbourhood_wordcloud(option)


def get_data_table(option):
    """Cache listings data table for given ward"""
    listings_helper = ListingsHelper(option)
    return listings_helper.get_data_table()

def process_neighbourhood_overviews(option):
    """Cache processed text data"""
    neighbourhoods_helper = get_neighbourhoods_helper()
    return neighbourhoods_helper.get_filtered_neighbourhood_overviews(option)


neighbourhoods_helper = get_neighbourhoods_helper()
ward_options = neighbourhoods_helper.get_ward_options()

st.set_page_config(layout="wide")

st.sidebar.markdown("# Airbnb Listings Analysis Dashboard") 
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



filtered_neighbourhoods, hood_metrics, hood_deltas = get_neighbourhood_data(option)
filtered_listings, listing_metrics, listing_deltas = get_listings_data(option)
host_metrics, global_host_metrics, host_deltas = get_host_data(option, filtered_listings)

overall_sentiment = hood_metrics['mode_sentiment'].title() if hood_metrics['mode_sentiment'] else "N/A"


st.sidebar.divider()
if option:
    st.sidebar.markdown(f"### {option} Summary")
else:
    st.sidebar.markdown("### Cape Town Summary")
st.sidebar.markdown(f"Longitude: :blue-background[{longitude:.5f}]")
st.sidebar.markdown(f"Latitude: :blue-background[{latitude:.5f}]")
st.sidebar.markdown(f"Total Hosts: :blue-background[{listing_metrics['total_hosts']}]")
st.sidebar.markdown(f"Total Listings: :blue-background[{listing_metrics['total_listings']}]")
st.sidebar.markdown(f"Lowest Rating: :blue-background[:red[{listing_metrics['min_rating']: .1f} stars]]")
st.sidebar.markdown(f"Highest Rating: :blue-background[:green[{listing_metrics['max_rating']: .1f} stars]]")
st.sidebar.markdown(f"Overall Sentiment :blue-background[{overall_sentiment}]")
st.space(size="small")
st.sidebar.divider()
st.sidebar.markdown("### About this Dashboard")
st.sidebar.markdown("This is a dashboard that displays Airbnb listings in Cape Town, South Africa. The data is sourced from [Inside Airbnb](http://insideairbnb.com/get-the-data.html) and is updated monthly.")    

st.markdown("# Airbnb Listings Analysis Dashboard")
st.markdown("## Prepared for Cape Town, South Africa")
st.markdown("### Overall Sentiments by User Reviews")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Positive Reviews (%)",
    f"{hood_metrics['positive_reviews_percent']:.2f}%",
    f"{hood_deltas['positive_reviews_percent_delta']:.2f}"          
)
col2.metric("Negative Reviews (%)",
    f"{hood_metrics['negative_reviews_percent']:.2f}%",  
    f"{hood_deltas['negative_reviews_percent_delta']:.2f}"  
)
col3.metric("Neutral Reviews (%)",
    f"{hood_metrics['neutral_reviews_percent']:.2f}%",  
    f"{hood_deltas['neutral_reviews_percent_delta']:.2f}"  
)
col4.metric("Overall Sentiment Score (-1 to +1)",
    f"{hood_metrics['overall_score']:.2f}", 
    f"{hood_deltas['overall_score_delta']:.2f}", 
)

with st.expander("Price Metrics", expanded=False):
    st.markdown("### Price Metrics")
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
        "Average Rating", 
        f"{listing_metrics['average_rating']:.1f} star(s)",
        f"{listing_deltas['average_rating_delta']:.1f} star(s)" 
        )
   

with st.expander("Occupancy & Revenue Metrics", expanded=False):  
    st.markdown("### Occupancy & Revenue Metrics")
    st.markdown(
        """
        Key Airbnb occupancy and revenue metrics for selected ward vs Cape Town overall:
        - **Avg. Occupancy Rate** (with Cape Town difference)
        - **Avg. Monthly Revenue** (with Cape Town difference)  
        """
    )   
    col1, col2 = st.columns(2)
    col1.metric(
        "Average Occupancy Rate", 
        f"{listing_metrics['average_occupancy']:.2f}%",
        f"{listing_deltas['average_occupancy_delta']:.2f}%")
    col2.metric(
        "Average Monthly Revenue", 
        f"ZAR {listing_metrics['average_revenue']:.2f}",
        f"{listing_deltas['average_revenue_delta']:.2f}"
    )

# Display host metrics
with st.expander("Host Metrics", expanded=False):
    st.markdown("### Host Metrics")
    st.markdown(
        """
        Key Airbnb host metrics for selected ward vs Cape Town overall:
        - **Avg. Host Response Rate** (with Cape Town difference)
        - **Avg. Host Acceptance Rate** (with Cape Town difference)  
        - **Verified Hosts (%)** (with Cape Town difference)
        - **Superhosts (%)** (with Cape Town difference)
        """
    )   
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

# Display listing type breakdown
with st.expander("Listings & Room Type Breakdown", expanded=False):
    st.markdown("### Listings by Room Type and Property Type")
    st.markdown(
        """
        Sunburst chart showing Airbnb listings by room type and property type.
        - **Size**: Number of listings per category
        - **Color**: Average estimated revenue per listing (Viridis scale)
        """
    )

    fig = get_tree_chart(option)
    st.plotly_chart(fig, use_container_width=True)

with st.expander("Neighbourhood Overview Word Cloud", expanded=False):
    st.markdown("### Neighbourhood Overview Word Cloud")
    st.markdown(
        """
        Word cloud generated from Airbnb neighbourhood overviews.
        - **Larger Words**: More frequently mentioned terms in overviews
        - **Stopwords Removed**: Common words filtered out for clarity
        """
    )
    svg = get_wordcloud_svg(option)
    if svg:
        centered_html = f"""
        <div style="display: flex; justify-content: center; align-items: center;">
            {svg}
        </div>
        """
        components.html(centered_html, width='stretch', height=600, scrolling=False)

# Display folium map and lisings data table
with st.container():
    st.markdown("## Listings Map and Data Table")
    st.markdown("""
        <style>
            iframe {
                border-radius: 15px;
            }
        </style>
        """, 
        unsafe_allow_html=True
    )
    col1, col2 = st.columns([45, 55], vertical_alignment="top")
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
        data_table = get_data_table(option)
        st.markdown("### Listings Data Table")
        st.markdown(
            """
            Data table of Airbnb listings in the selected ward.
            - **Price**: Price per night in ZAR
            - **Rating**: Average review score rating
            """
        )
        st.dataframe(data_table, width='stretch')
   
    with col2:
        st.markdown("### Listings Map")
        st.markdown(
            """
            Map showing Airbnb listings in the selected ward.
            - **Markers**: Each marker represents a listing
            - **Popup Info**: Click on a marker to see price and rating details
            """
        )
        st_data = st_folium(n, width="stretch", height=400)  