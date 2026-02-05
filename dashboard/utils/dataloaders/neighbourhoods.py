import re
import json
import pandas as pd
from .universal import LoadNormalisedData, analyzer


class NeighbourhoodsDataLoader(LoadNormalisedData):

    def __init__(self):
        super().__init__()

    def transform_neighbourhoods(self):
        """Transform neighbourhood data by merging with ward information."""
        # Create a copy of wards to avoid modifying global variable
        wards_df = self.wards.copy()
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

    def transform_neighbourhood_overviews(self):
        """Transform neighbourhood overviews in preparation for visualisations and metrics."""

        df = self.neighbourhood_overviews.copy()
        df = df.dropna(subset=['neighbourhood_id', 'neighbourhood_overview'])
        df['neighbourhood_overview'] = df['neighbourhood_overview'].str.strip().str.lower()
        df['cleaned_overview'] = df['neighbourhood_overview'].apply(self._preprocess_text)
        df['sentiment_scores'] = df['cleaned_overview'].apply(lambda x: analyzer.polarity_scores(x))
        df['compound_sentiment'] = df['sentiment_scores'].apply(lambda x: x['compound'])
        df['sentiment_label'] = df['compound_sentiment'].apply(
            lambda x: 'positive' if x >= 0.05 else ('negative' if x <= -0.05 else 'neutral')
        )

        return df

