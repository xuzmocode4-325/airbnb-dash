import re
import pandas as pd
import plotly.express as px


class DashboardProcesses:
    """Utility class for dashboard data processing and filtering operations."""

    def _extract_num(self, ward):
        """Extract numeric ID from ward name string.
        
        Args:
            ward: str, ward name in format 'Ward {num}'
            
        Returns:
            int: ward number or float('inf') if no match found
        """
        match = re.search(r'Ward (\d+)', ward)
        return int(match.group(1)) if match else float('inf')     

    def sort_wards(self, df, column_name):
        """Returns a sorted list of unique 'Ward {num}' items by extracting and sorting numerically.
        
        Args:
            df: pandas DataFrame
            column_name: str, name of column containing 'Ward {num}' format
        
        Returns:
            list: sorted wards in format ['Ward 1', 'Ward 2', 'Ward 10', ...]
        """
        if df.empty or column_name not in df.columns:
            return []
        
        # Extract unique ward values, filtering out nulls
        wards = df[column_name].dropna().unique()
        
        # Sort numerically by extracted ward number
        sorted_wards = sorted(wards, key=self._extract_num)
        return sorted_wards
    
    def filter_ward_by_option(self, df, option):
        """Filter dataframe by ward name option.
        
        Args:
            df: pandas DataFrame with 'name' column
            option: str or None, ward name to filter by
            
        Returns:
            pandas DataFrame: filtered or original dataframe
        """
        if not option or df.empty:
            return df
        return df[df['name'] == option]
    
    
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
    
    def filter_hosts_by_ward(self, df, listings_info, option=None):
        """Filter hosts dataframe to include only hosts from selected ward.
        
        Args:
            df: pandas DataFrame containing host data
            listings_info: pandas DataFrame containing listings information
            option: str or None, ward selection (used to determine if filtering should occur)
            
        Returns:
            pandas DataFrame: filtered or original hosts dataframe
        """
        # If no ward is selected or dataframe is empty, return all hosts
        if not option or df.empty:
            return df
        
        # Extract host IDs from the filtered listings
        ward_hosts = listings_info['host_id'].unique()
        
        # If no hosts found in the ward, return empty dataframe with same structure
        if len(ward_hosts) == 0:
            return df[df['host_id'].isin([])]
        
        # Filter hosts to only those with listings in the selected ward
        return df[df['host_id'].isin(ward_hosts)]

    
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
    

    def get_metrics_for_ward_hosts(self, df):
        """Calculate key metrics for hosts in the selected ward.
        
        Args:
            df: pandas DataFrame containing host data
            
        Returns:
            dict: metrics including total hosts, response/acceptance rates, and verification percentages
        """
        if df.empty:
            return {
                'total_hosts': 0,
                'mean_response_rate': 0.0,
                'mean_acceptance_rate': 0.0,
                'super_hosts_percent': 0.0,
                'verified_hosts_percent': 0.0
            }
        
        else:
            total_hosts = df['host_id'].nunique()
            mean_response_rate = df['host_response_rate'].mean() if 'host_response_rate' in df.columns else 0.0
            mean_acceptance_rate = df['host_acceptance_rate'].mean() if 'host_acceptance_rate' in df.columns else 0.0

            num_superhosts = df['host_is_superhost'].sum() if 'host_is_superhost' in df.columns else 0
            #print("Number of superhosts:", num_superhosts)
            percent_superhosts = (num_superhosts / total_hosts) * 100
            #print("Percent superhosts:", percent_superhosts)
            
            num_verified_hosts = df['host_identity_verified'].sum() if 'host_identity_verified' in df.columns else 0
            #print("Number of verified hosts:", num_verified_hosts)
            percent_verified_hosts = (num_verified_hosts / total_hosts) * 100
            #print("Percent verified hosts:", percent_verified_hosts)

            # Calculate percentages
            #super_hosts_percent = su

            metrics = {
                'total_hosts': total_hosts,
                'mean_response_rate': mean_response_rate,
                'mean_acceptance_rate': mean_acceptance_rate,
                'super_hosts_count': num_superhosts,
                'verified_hosts_count': num_verified_hosts,
                'super_hosts_percent': percent_superhosts,
                'verified_hosts_percent': percent_verified_hosts
            }

            return metrics
        
      # Alias for global host metrics
    def get_global_host_metrics(self, df):
        """Alias for get_metrics_for_ward_hosts to calculate global host metrics.
        
        Args:
            df: pandas DataFrame containing host data
            
        Returns:
            dict: global host metrics
        """
        return self.get_metrics_for_ward_hosts(df)

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


    def make_sunburst_chart(self, df):
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

        fig.update_traces(
            marker=dict(
                line=dict(width=0)  # Remove all borders
            )
        )

        return fig