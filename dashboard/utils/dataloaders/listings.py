import pandas as pd
from .universal import LoadNormalisedData

class ListingsDataLoader(LoadNormalisedData):
    def __init__(self):
        super().__init__()
        
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