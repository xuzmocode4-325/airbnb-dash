from wordcloud import WordCloud
import matplotlib.pyplot as plt
from .universal import DashboardProcesses

# Neighbourhoods processing functions
class NeighbourhoodsProcesses(DashboardProcesses):
    def __init__(self):
        super().__init__()


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
    

    def filter_neighbourhood_reviews_by_ward(self, df, option):
        """Filter dataframe by ward name option

        Args:
            df: pandas DataFramwe with 'neighbourhood_id' column
            option: str or None, ward name to filter by

        Returns:
            pandas DataFrame: filtered or original
        """ 

        if not option or df.empty:
            return df
        ward_id = self._extract_num(option)
        if ward_id == float('inf'):
            return df
        return df[df['neighbourhood_id'] == ward_id]
    

    def get_neighbourhood_sentiment_metrics(self, df):
        """Calculates sentiment metrics for the given ward's listings.
        
        Args:
            df: pandas DataFrame containing listings for a specific ward
            
        Returns:
            dict: metrics including overall sentiment score and the proportion of positive, negative and neutral reviews
        """
        if df.empty:
            return {
                'overall_score': 0.0,
                'positive_reviews_percent': 0.0,
                'negative_reviews_percent': 0.0,
                'neutral_reviews_percent': 0.0,
            }
        else: 
            mode_sentiment = df['sentiment_label'].mode()
            sentiment_proportions = df['sentiment_label'].value_counts() / len(df)

            # Extract each sentiment as a discrete variable
            positive = sentiment_proportions.get('positive', 0)
            negative = sentiment_proportions.get('negative', 0)
            neutral = sentiment_proportions.get('neutral', 0)

            # Overall sentiment score
            overall_score = df['compound_sentiment'].mean()

            return {
                'overall_score': overall_score,
                'positive_reviews_percent': positive,
                'negative_reviews_percent': negative,
                'neutral_reviews_percent': neutral,
                'mode_sentiment': mode_sentiment.iloc[0] if not mode_sentiment.empty else None
            }


    def get_global_sentiment_metrics(self, df):
        """Calculate global sentiment metrics across all wards.
        
        Args:
            df: pandas DataFrame containing sentiment data       
        Returns:
            dict: global sentiment metrics
        """
        return self.get_neighbourhood_sentiment_metrics(df)
    

    def make_neighbourhood_wordcloud(self, df):
        """Generate a word cloud SVG for the specified ward option.

        Args:
            df: pandas DataFrame with 'cleaned_overview' column
        Returns:
            str: SVG string or None if DataFrame is empty or column is missing     
        """
        if df.empty or 'cleaned_overview' not in df.columns:
            return None
        text = ' '.join(df['cleaned_overview'].dropna())
        if not text.strip():
            return None
        wc = WordCloud(
            width=900, height=500, 
            background_color='#0D1116',
            colormap='viridis', max_words=100
        ).generate(text)

        # Return SVG string
        svg_string = wc.to_svg(embed_font=True)
        return svg_string