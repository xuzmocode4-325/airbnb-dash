
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


def get_neighbourhood_data(option):
    """Cache neighbourhood data based on selected ward"""
    neighbourhoods_helper = get_neighbourhoods_helper()
    filtered_neighbourhoods = neighbourhoods_helper.get_filtered_neighbourhood(option)
    hood_metrics = neighbourhoods_helper.get_neighbourhood_sentiment_metrics(option)
    hood_deltas = neighbourhoods_helper.get_neighbourhood_sentiment_deltas(option)
    return filtered_neighbourhoods, hood_metrics, hood_deltas


def get_listings_data(option):
    """Cache listings data based on selected ward"""
    listings_helper = ListingsHelper(option)
    filtered_listings = listings_helper.get_filtered_listings()
    listing_metrics = listings_helper.get_listing_metrics()
    listing_deltas = listings_helper.get_listing_deltas()
    return filtered_listings, listing_metrics, listing_deltas

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

# Language translations
TRANSLATIONS = {
    "en": {
        "title": "Airbnb Listings Analysis Dashboard",
        "language": "Language",
        "select_ward": "Select Ward",
        "select_ward_placeholder": "Select a ward",
        "summary": "Summary",
        "longitude": "Longitude",
        "latitude": "Latitude",
        "total_hosts": "Total Hosts",
        "total_listings": "Total Listings",
        "lowest_rating": "Lowest Rating",
        "highest_rating": "Highest Rating",
        "overall_sentiment": "Overall Sentiment",
        "cape_town_summary": "Cape Town Summary",
        "about_dashboard": "About this Dashboard",
        "about_text": "This is a dashboard that displays Airbnb listings in Cape Town, South Africa. The data is sourced from Inside Airbnb and is updated monthly.",
        "main_title": "Airbnb Listings Analysis Dashboard",
        "main_subtitle": "Prepared for Cape Town, South Africa",
        "sentiments_heading": "Overall Sentiments by User Reviews",
        "positive_reviews": "Positive Reviews (%)",
        "negative_reviews": "Negative Reviews (%)",
        "neutral_reviews": "Neutral Reviews (%)",
        "sentiment_score": "Overall Sentiment Score (-1 to +1)",
        "price_metrics": "Price Metrics",
        "price_metrics_desc": "Key Airbnb metrics for selected ward vs Cape Town overall:\n- **Lowest/Highest Price** in ward\n- **Avg Price** (with Cape Town difference)\n- **Avg Rating** (with Cape Town difference)",
        "lowest_price": "Lowest Price",
        "highest_price": "Highest Price",
        "average_price": "Average Price",
        "average_rating": "Average Rating",
        "occupancy_revenue": "Occupancy & Revenue Metrics",
        "occupancy_revenue_desc": "Key Airbnb occupancy and revenue metrics for selected ward vs Cape Town overall:\n- **Avg. Occupancy Rate** (with Cape Town difference)\n- **Avg. Monthly Revenue** (with Cape Town difference)",
        "avg_occupancy": "Average Occupancy Rate",
        "avg_monthly_revenue": "Average Monthly Revenue",
        "host_metrics": "Host Metrics",
        "host_metrics_desc": "Key Airbnb host metrics for selected ward vs Cape Town overall:\n- **Avg. Host Response Rate** (with Cape Town difference)\n- **Avg. Host Acceptance Rate** (with Cape Town difference)\n- **Verified Hosts (%)** (with Cape Town difference)\n- **Superhosts (%)** (with Cape Town difference)",
        "avg_response_rate": "Avg. Host Response Rate",
        "avg_acceptance_rate": "Avg. Host Acceptance Rate",
        "verified_hosts": "Verified Hosts (%)",
        "superhosts": "Superhosts (%)",
        "listings_breakdown": "Listings & Room Type Breakdown",
        "listings_breakdown_heading": "Listings by Room Type and Property Type",
        "listings_breakdown_desc": "Sunburst chart showing Airbnb listings by room type and property type.\n- **Size**: Number of listings per category\n- **Color**: Average estimated revenue per listing (Viridis scale)",
        "wordcloud": "Neighbourhood Overview Word Cloud",
        "wordcloud_desc": "Word cloud generated from Airbnb neighbourhood overviews.\n- **Larger Words**: More frequently mentioned terms in overviews\n- **Stopwords Removed**: Common words filtered out for clarity",
        "listings_map_title": "Listings Map and Data Table",
        "listings_data_table": "Listings Data Table",
        "listings_data_desc": "Data table of Airbnb listings in the selected ward.\n- **Price**: Price per night in ZAR\n- **Rating**: Average review score rating",
        "listings_map": "Listings Map",
        "listings_map_desc": "Map showing Airbnb listings in the selected ward.\n- **Markers**: Each marker represents a listing\n- **Popup Info**: Click on a marker to see price and rating details",
    },
    "de": {
        "title": "Airbnb-Angebote Analyse Dashboard",
        "language": "Sprache",
        "select_ward": "Wählen Sie Ward",
        "select_ward_placeholder": "Wählen Sie einen Ward",
        "summary": "Zusammenfassung",
        "longitude": "Längengrad",
        "latitude": "Breitengrad",
        "total_hosts": "Gesamtzahl der Gastgeber",
        "total_listings": "Gesamtzahl der Angebote",
        "lowest_rating": "Niedrigste Bewertung",
        "highest_rating": "Höchste Bewertung",
        "overall_sentiment": "Gesamtstimmung",
        "cape_town_summary": "Kapstadt Zusammenfassung",
        "about_dashboard": "Über dieses Dashboard",
        "about_text": "Dies ist ein Dashboard, das Airbnb-Angebote in Kapstadt, Südafrika anzeigt. Die Daten stammen von Inside Airbnb und werden monatlich aktualisiert.",
        "main_title": "Airbnb-Angebote Analyse Dashboard",
        "main_subtitle": "Vorbereitet für Kapstadt, Südafrika",
        "sentiments_heading": "Gesamtstimmung nach Benutzerbewertungen",
        "positive_reviews": "Positive Bewertungen (%)",
        "negative_reviews": "Negative Bewertungen (%)",
        "neutral_reviews": "Neutrale Bewertungen (%)",
        "sentiment_score": "Gesamtstimmungs-Score (-1 bis +1)",
        "price_metrics": "Preismetriken",
        "price_metrics_desc": "Wichtige Airbnb-Metriken für ausgewählten Ward vs. Kapstadt insgesamt:\n- **Niedrigster/Höchster Preis** im Ward\n- **Durchschnittspreis** (mit Kapstadt-Differenz)\n- **Durchschnittliche Bewertung** (mit Kapstadt-Differenz)",
        "lowest_price": "Niedrigster Preis",
        "highest_price": "Höchster Preis",
        "average_price": "Durchschnittspreis",
        "average_rating": "Durchschnittliche Bewertung",
        "occupancy_revenue": "Auslastungs- und Umsatzmetriken",
        "occupancy_revenue_desc": "Wichtige Airbnb-Auslastungs- und Umsatzmetriken für ausgewählten Ward vs. Kapstadt insgesamt:\n- **Durchschn. Auslastungsrate** (mit Kapstadt-Differenz)\n- **Durchschn. Monatlicher Umsatz** (mit Kapstadt-Differenz)",
        "avg_occupancy": "Durchschnittliche Auslastungsrate",
        "avg_monthly_revenue": "Durchschnittlicher Monatlicher Umsatz",
        "host_metrics": "Gastgeber-Metriken",
        "host_metrics_desc": "Wichtige Airbnb-Gastgeber-Metriken für ausgewählten Ward vs. Kapstadt insgesamt:\n- **Durchschn. Gastgeber-Reaktionsrate** (mit Kapstadt-Differenz)\n- **Durchschn. Gastgeber-Annahmerate** (mit Kapstadt-Differenz)\n- **Verifizierte Gastgeber (%)** (mit Kapstadt-Differenz)\n- **Superhosts (%)** (mit Kapstadt-Differenz)",
        "avg_response_rate": "Durchschn. Gastgeber-Reaktionsrate",
        "avg_acceptance_rate": "Durchschn. Gastgeber-Annahmerate",
        "verified_hosts": "Verifizierte Gastgeber (%)",
        "superhosts": "Superhosts (%)",
        "listings_breakdown": "Angebote und Zimmertyp-Aufschlüsselung",
        "listings_breakdown_heading": "Angebote nach Zimmertyp und Immobilientyp",
        "listings_breakdown_desc": "Sunburst-Diagramm mit Airbnb-Angeboten nach Zimmertyp und Immobilientyp.\n- **Größe**: Anzahl der Angebote pro Kategorie\n- **Farbe**: Durchschnittlicher geschätzter Umsatz pro Angebot (Viridis-Skala)",
        "wordcloud": "Nachbarschafts-Übersichts-Wort-Wolke",
        "wordcloud_desc": "Wort-Wolke aus Airbnb-Nachbarschaftsübersichten.\n- **Größere Wörter**: Häufiger erwähnte Begriffe in Übersichten\n- **Stoppwörter entfernt**: Häufige Wörter zur Klarheit herausgefiltert",
        "listings_map_title": "Angebotskarte und Datentabelle",
        "listings_data_table": "Angebots-Datentabelle",
        "listings_data_desc": "Datentabelle der Airbnb-Angebote im ausgewählten Ward.\n- **Preis**: Preis pro Nacht in ZAR\n- **Bewertung**: Durchschnittliche Bewertung",
        "listings_map": "Angebotskarte",
        "listings_map_desc": "Karte mit Airbnb-Angeboten im ausgewählten Ward.\n- **Markierungen**: Jede Markierung stellt ein Angebot dar\n- **Popup-Info**: Klicken Sie auf eine Markierung, um Preis- und Bewertungsdetails zu sehen",
    }
}

# Initialize language in session state
if 'language' not in st.session_state:
    st.session_state.language = 'en'

def get_text(key):
    """Get translated text based on current language"""
    return TRANSLATIONS[st.session_state.language].get(key, key)

st.sidebar.markdown(f"# {get_text('title')}") 

# Language toggle
st.sidebar.radio(
    get_text("language"),
    options=["English", "Deutsch"],
    format_func=lambda x: x,
    index=0 if st.session_state.language == 'en' else 1,
    key='lang_toggle',
    on_change=lambda: st.session_state.update(language='en' if st.session_state.lang_toggle == 'English' else 'de')
)

st.sidebar.divider()

# Neighbourhood selection dropdown
option = st.sidebar.selectbox(
    get_text("select_ward"), 
    index = None,
    placeholder=get_text("select_ward_placeholder"),
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
    st.sidebar.markdown(f"### {get_text('summary')} - {option}")
else:
    st.sidebar.markdown(f"### {get_text('cape_town_summary')}")
st.sidebar.markdown(f"{get_text('longitude')}: :blue-background[{longitude:.5f}]")
st.sidebar.markdown(f"{get_text('latitude')}: :blue-background[{latitude:.5f}]")
st.sidebar.markdown(f"{get_text('total_hosts')}: :blue-background[{listing_metrics['total_hosts']}]")
st.sidebar.markdown(f"{get_text('total_listings')}: :blue-background[{listing_metrics['total_listings']}]")
st.sidebar.markdown(f"{get_text('lowest_rating')}: :blue-background[:red[{listing_metrics['min_rating']: .1f} stars]]")
st.sidebar.markdown(f"{get_text('highest_rating')}: :blue-background[:green[{listing_metrics['max_rating']: .1f} stars]]")
st.sidebar.markdown(f"{get_text('overall_sentiment')} :blue-background[{overall_sentiment}]")
st.space(size="small")
st.sidebar.divider()
st.sidebar.markdown(f"### {get_text('about_dashboard')}")
st.sidebar.markdown(get_text("about_text"))    

st.markdown(f"# {get_text('main_title')}")
st.markdown(f"## {get_text('main_subtitle')}")
st.markdown(f"### {get_text('sentiments_heading')}")

col1, col2, col3, col4 = st.columns(4)
col1.metric(get_text('positive_reviews'),
    f"{hood_metrics['positive_reviews_percent']:.2f}%",
    f"{hood_deltas['positive_reviews_percent_delta']:.2f}"          
)
col2.metric(get_text('negative_reviews'),
    f"{hood_metrics['negative_reviews_percent']:.2f}%",  
    f"{hood_deltas['negative_reviews_percent_delta']:.2f}"  
)
col3.metric(get_text('neutral_reviews'),
    f"{hood_metrics['neutral_reviews_percent']:.2f}%",  
    f"{hood_deltas['neutral_reviews_percent_delta']:.2f}"  
)
col4.metric(get_text('sentiment_score'),
    f"{hood_metrics['overall_score']:.2f}", 
    f"{hood_deltas['overall_score_delta']:.2f}", 
)

with st.expander(get_text('price_metrics'), expanded=False):
    st.markdown(f"### {get_text('price_metrics')}")
    st.markdown(get_text('price_metrics_desc'))
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        get_text('lowest_price'), 
        f"ZAR {listing_metrics['min_price']:.2f}"
    )
    col2.metric(
        get_text('highest_price'), 
        f"ZAR {listing_metrics['max_price']:.2f}",
    )
    col3.metric(
        get_text('average_price'), 
        f"ZAR {listing_metrics['average_price']:.2f}",
        f"{listing_deltas['average_price_delta']:.2f} ZAR")
    col4.metric(
        get_text('average_rating'), 
        f"{listing_metrics['average_rating']:.1f} star(s)",
        f"{listing_deltas['average_rating_delta']:.1f} star(s)" 
        )
   

with st.expander(get_text('occupancy_revenue'), expanded=False):  
    st.markdown(f"### {get_text('occupancy_revenue')}")
    st.markdown(get_text('occupancy_revenue_desc'))
    col1, col2 = st.columns(2)
    col1.metric(
        get_text('avg_occupancy'), 
        f"{listing_metrics['average_occupancy']:.2f}%",
        f"{listing_deltas['average_occupancy_delta']:.2f}%")
    col2.metric(
        get_text('avg_monthly_revenue'), 
        f"ZAR {listing_metrics['average_revenue']:.2f}",
        f"{listing_deltas['average_revenue_delta']:.2f}"
    )

# Display host metrics
with st.expander(get_text('host_metrics'), expanded=False):
    st.markdown(f"### {get_text('host_metrics')}")
    st.markdown(get_text('host_metrics_desc'))
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        get_text('avg_response_rate'), 
        f"{host_metrics['mean_response_rate']:.2f}%",
        f"{host_deltas['mean_response_rate_delta']:.2f}%")
    col2.metric(
        get_text('avg_acceptance_rate'), 
        f"{host_metrics['mean_acceptance_rate']:.2f}%",
        f"{host_deltas['mean_acceptance_rate_delta']:.2f}%")
    col3.metric(
        get_text('verified_hosts'), 
        f"{host_metrics['verified_hosts_percent']:.2f}%",
        f"{host_deltas['verified_hosts_percent_delta']:.2f}%")
    col4.metric(
        get_text('superhosts'), 
        f"{host_metrics['super_hosts_percent']:.2f}%",
        f"{host_deltas['super_hosts_percent_delta']:.2f}%"
    )

# Display listing type breakdown
with st.expander(get_text('listings_breakdown'), expanded=False):
    st.markdown(f"### {get_text('listings_breakdown_heading')}")
    st.markdown(get_text('listings_breakdown_desc'))

    fig = get_tree_chart(option)
    st.plotly_chart(fig, use_container_width=True)

with st.expander(get_text('wordcloud'), expanded=False):
    st.markdown(f"### {get_text('wordcloud')}")
    st.markdown(get_text('wordcloud_desc'))
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
    st.markdown(f"## {get_text('listings_map_title')}")
    st.markdown("""
        <style>
            iframe {
                border-radius: 15px;
            }
        </style>
        """, 
        unsafe_allow_html=True
    )
   
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
    
    st.markdown(f"### {get_text('listings_map')}")
    st.markdown(get_text('listings_map_desc'))
    st_data = st_folium(n, width="stretch", height=400)  

    data_table = get_data_table(option)
    st.markdown(f"### {get_text('listings_data_table')}")
    st.markdown(get_text('listings_data_desc'))
    st.dataframe(data_table, width='stretch')