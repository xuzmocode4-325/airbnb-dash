import os
import re
import sys
import json
import nltk
import pandas as pd
import streamlit as st
from pathlib import Path
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

nltk.download(['stopwords', 'wordnet', 'omw-1.4'])

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
analyzer = SentimentIntensityAnalyzer()

project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from src.normalisers import NormaliseReviews, NormaliseListings

# Load data files
@st.cache_data
def load_base_data():
    """Load and return all base data files"""
    data_dir = project_root / 'data'
    reviews = pd.read_csv(data_dir / 'reviews.csv.gz')
    listings = pd.read_csv(data_dir / 'listings.csv.gz')
    calendar = pd.read_csv(data_dir / 'calendar.csv.gz')
    wards = pd.read_csv(data_dir / 'wards.csv')
    with open(data_dir / 'contractions.json') as f:
        contractions = json.load(f)
    return reviews, listings, calendar, wards, contractions

reviews, listings, calendar, wards, contractions = load_base_data()


def normalize_data(reviews, listings):
    """Normalize reviews and listings data"""
    normalise_reviews = NormaliseReviews(reviews)
    review_comments = normalise_reviews.normalise_reviews()
    
    normalise_listings = NormaliseListings(listings)
    unique_hosts = normalise_listings.normalise_hosts()
    unique_listings = normalise_listings.normalise_listings()
    neighbourhoods = normalise_listings.normalise_neighbourhoods()
    listing_reviews = normalise_listings.normalise_listing_reviews()
    neighbourhood_overviews = normalise_listings.normalise_neighbourhood_overview()
    
    return {
        'review_comments': review_comments,
        'unique_hosts': unique_hosts,
        'unique_listings': unique_listings,
        'neighbourhoods': neighbourhoods,
        'listing_reviews': listing_reviews,
        'neighbourhood_overviews': neighbourhood_overviews
    }


normalized_data = normalize_data(reviews, listings)


class LoadNormalisedData:
    def __init__(self):
        self.wards = wards
        self.reviews = normalized_data['review_comments']
        self.hosts = normalized_data['unique_hosts']
        self.listings = normalized_data['unique_listings']
        self.neighbourhoods = normalized_data['neighbourhoods']
        self.listing_reviews = normalized_data['listing_reviews']
        self.neighbourhood_overviews = normalized_data['neighbourhood_overviews']
        self.contractions = contractions     

    def _preprocess_text(self, text):
        for contraction, expansion in self.contractions.items():
            text = text.replace(contraction, expansion)
        text = re.sub(r'[^a-zA-Z\s]', '', str(text).lower())
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'@\w+|#\w+', '', text)  # Remove mentions and hashtags
        tokens = text.split()
        tokens = [lemmatizer.lemmatize(w) for w in tokens if w not in stop_words and len(w) > 2]
        return ' '.join(tokens)


    def _fill_nan_coordinates(self, new_wards):
        """Fill missing coordinates with mean values from listings data."""
        # Get neighbourhood_ids with NaN latitude/longitude
        nan_wards = new_wards[new_wards['latitude'].isna()]['neighbourhood_id'].unique()

        if len(nan_wards) == 0:
            return new_wards
        
        # Calculate mean coordinates for all neighbourhoods at once (vectorized)
        coords_by_neighbourhood = self.listings.groupby('neighbourhood_id')[['latitude', 'longitude']].mean()
        
        # For each ward with NaN coordinates, fill with mean from listings
        for ward_id in nan_wards:
            if ward_id in coords_by_neighbourhood.index:
                new_wards.loc[new_wards['neighbourhood_id'] == ward_id, 'latitude'] = coords_by_neighbourhood.loc[ward_id, 'latitude']
                new_wards.loc[new_wards['neighbourhood_id'] == ward_id, 'longitude'] = coords_by_neighbourhood.loc[ward_id, 'longitude']

        return new_wards 