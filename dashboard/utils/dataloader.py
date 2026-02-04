import os
import sys
import pandas as pd
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from src.normalisers import NormaliseReviews, NormaliseListings

# Load data files
data_dir = project_root / 'data'
reviews = pd.read_csv(data_dir / 'reviews.csv.gz')
listings = pd.read_csv(data_dir / 'listings.csv.gz')
calendar = pd.read_csv(data_dir / 'calendar.csv.gz')
wards = pd.read_csv(data_dir / 'wards.csv')

# Reviews normalization
normalise_reviews = NormaliseReviews(reviews)
review_comments = normalise_reviews.normalise_reviews()

# Listings normalization
normalise_listings = NormaliseListings(listings)
unique_hosts = normalise_listings.normalise_hosts()
unique_listings = normalise_listings.normalise_listings()
neighbourhoods = normalise_listings.normalise_neighbourhoods()
listing_reviews = normalise_listings.normalise_listing_reviews()
neighbourhood_overviews = normalise_listings.normalise_neighbourhood_overview()


class TransformedData:
    def __init__(self):
        self.reviews = review_comments
        self.hosts = unique_hosts
        self.listings = unique_listings
        self.neighbourhoods = neighbourhoods
        self.listing_reviews = listing_reviews
        self.neighbourhood_overviews = neighbourhood_overviews

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


    def transform_listings_with_ratings(self):
        """Merge listings with review scores and filter valid records."""
        listings_x_ratings = pd.merge(
            self.listings,
            self.listing_reviews, 
            on='listing_id',
            how='left'
        )
        
        # Filter out listings without price or rating data
        listings_x_ratings = listings_x_ratings.dropna(subset=['price_usd', 'review_scores_rating'])
        return listings_x_ratings
    
    def transform_neighbourhoods(self):
        """Transform neighbourhood data by merging with ward information."""
        # Create a copy of wards to avoid modifying global variable
        wards_df = wards.copy()
        wards_df['neighbourhood_id'] = wards_df['Name'].str.replace('Ward', '').str.strip().astype(int)
        
        new_wards = pd.merge(
            self.neighbourhoods,
            wards_df,
            on='neighbourhood_id',
            how='left'
        )

        # Drop redundant column if it exists
        if 'neighbourhood_cleansed' in new_wards.columns:
            new_wards = new_wards.drop(columns=['neighbourhood_cleansed'])
        
        # Standardize column names
        new_wards.columns = [col.lower() for col in new_wards.columns]
        new_wards = new_wards.drop_duplicates()
        new_wards = self._fill_nan_coordinates(new_wards)
        new_wards = new_wards.sort_values('neighbourhood_id').reset_index(drop=True)
        
        # Fill missing names with "Ward {id}"
        mask = new_wards['name'].isna()
        new_wards.loc[mask, 'name'] = new_wards.loc[mask, 'neighbourhood_id'].apply(lambda x: f"Ward {x}")

        return new_wards
    
    def transform_hosts(self):
        """Clean and deduplicate hosts data."""
        drop_cols = [
            'host_name', 'host_location', 
            'host_has_profile_pic', 'host_about', 'host_verifications'   
        ]
        
        # Only drop columns that actually exist
        existing_drop_cols = [col for col in drop_cols if col in self.hosts.columns]
        hosts_cleaned = self.hosts.drop(columns=existing_drop_cols)
        
        # Deduplicate and reset index
        hosts_cleaned = hosts_cleaned.drop_duplicates(subset=['host_id']).reset_index(drop=True)

        return hosts_cleaned


    
    
    
        