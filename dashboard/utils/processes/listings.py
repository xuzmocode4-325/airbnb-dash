
import pandas as pd
import plotly.express as px
from .universal import DashboardProcesses

class ListingsProcesses(DashboardProcesses):
    def __init__(self):
        super().__init__()

    def filter_listings_by_ward(self, df, ward_name):
        """Filters the listings DataFrame to include only listings in the specified ward.
        
        Args:
            df: pandas DataFrame containing listings with a 'neighbourhood_id' column
            ward_name: str or None, name of the ward to filter by (e.g., 'Ward 1')
            
        Returns:
            pandas DataFrame: filtered listings in the specified ward
        """
        if not ward_name or df.empty:
            return df
        
        ward_id = self._extract_num(ward_name)
        if ward_id == float('inf'):
            return df
        
        return df[df['neighbourhood_id'] == ward_id]

    def get_metrics_for_ward_listings(self, df):
        """Calculates key metrics for the given ward's listings.
        
        Args:
            df: pandas DataFrame containing listings for a specific ward
            
        Returns:
            dict: metrics including average price, average rating, total listings, and total hosts
        """
        if df.empty:
            return {
                'average_price': 0.0,
                'average_rating': 0.0,
                'total_hosts': 0,
                'total_listings': 0,
                'min_price': 0.0,
                'max_price': 0.0,
                'min_rating': 0.0,
                'max_rating': 0.0,
                'average_occupancy': 0.0,
                'average_revenue': 0.0
            }
        
        else:
            # Calculate metrics, using 0 as default for missing values
            min_price = df['price_usd'].min() if not df['price_usd'].isna().all() else 0.0
            max_price = df['price_usd'].max() if not df['price_usd'].isna().all() else 0.0
            min_rating = df['review_scores_rating'].min() if not df['review_scores_rating'].isna().all() else 0.0
            max_rating = df['review_scores_rating'].max() if not df['review_scores_rating'].isna().all() else 0.0   
            average_price = df['price_usd'].mean() if not df['price_usd'].isna().all() else 0.0
            average_rating = df['review_scores_rating'].mean() if not df['review_scores_rating'].isna().all() else 0.0
            total_hosts = df['host_id'].nunique()
            total_listings = len(df)
            average_occupancy = df['estimated_occupancy_l365d'].mean() if not df['estimated_occupancy_l365d'].isna().all() else 0.0
            average_revenue = (df['estimated_revenue_l365d'].mean() / 12) if not df['estimated_revenue_l365d'].isna().all() else 0.0
           
            metrics = {
                'min_price': min_price,
                'max_price': max_price,
                'min_rating': min_rating,
                'max_rating': max_rating,
                'average_price': average_price,
                'average_occupancy': average_occupancy,
                'average_revenue': average_revenue,
                'average_rating': average_rating,
                'total_hosts': total_hosts,
                'total_listings': total_listings
            }
        return metrics
    

    def get_global_listing_metrics(self, df):
        """Calculate global listing metrics across all wards.
        
        Args:
            df: pandas DataFrame containing listing data       
        Returns:
            dict: global listing metrics
        """
        return self.get_metrics_for_ward_listings(df)
    

    def get_data_table(self, df):
        """Generate summary table of listings grouped by neighbourhood.
        
        Args:
            df: pandas DataFrame containing listings data
            
        Returns:
            pandas DataFrame: aggregated table with price, rating, and listing counts by ward
        """
        if df.empty:
            return pd.DataFrame(columns=["Price (ZAR)", "Average Rating (Stars)", "Total Listings"])
        
        # Filter out rows with missing price or rating data
        filtered_df = df[
            df['price_usd'].notna() & 
            df['review_scores_rating'].notna()
        ]
        
        if filtered_df.empty:
            return pd.DataFrame(columns=["Price (ZAR)", "Average Rating (Stars)", "Total Listings"])
        
        table = filtered_df.groupby('neighbourhood_id').agg({
            'price_usd': 'mean',
            'review_scores_rating': 'mean',
            'listing_id': 'count'
        }).sort_index(
            key=lambda x: x.astype(int), 
            ascending=True
        )
        
        table.index.name = "Ward"
        table.columns = ["Price (ZAR)", "Average Rating (Stars)", "Total Listings"]
        
        # Round numeric columns to specified decimal places
        table["Price (ZAR)"] = table["Price (ZAR)"].round(2)
        table["Average Rating (Stars)"] = table["Average Rating (Stars)"].apply(lambda x: f"{x:.1f}")
        
        return table


    def make_tree_chart(self, df):
        """Display sunburst chart of listings by room and property type.
        
        Args:
            df: pandas DataFrame containing listings with ratings
        """

        sunburst_data = df.groupby(['room_type', 'property_type']).agg({
            'listing_id': 'count',
            'estimated_revenue_l365d': 'mean'
        }).sort_values('listing_id', ascending=False).reset_index().rename(columns={
            'listing_id': 'count',
            'estimated_revenue_l365d': 'mean_revenue'
        })
        
        
        fig = px.treemap(
            sunburst_data,
            path=[px.Constant("listings"), 'room_type', 'property_type'],
            values='count',
            color='mean_revenue',
            color_continuous_scale='Viridis'
        )

        fig.update_layout(
            height=700,
            paper_bgcolor='#0D1116',
            plot_bgcolor='#0D1116',
            font=dict(color='white', size=14),
            margin=dict(t=50, l=50, r=50, b=50)
        )

        fig.update_coloraxes(colorbar_title_text="Average Annual Revenue")

        fig.update_traces(
            marker=dict(
                line=dict(width=0)  # Remove all borders
            )
        )

        return fig