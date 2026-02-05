
from  .universal import UIHelper


# Neighbourhood helper class
class NeighbourhoodsHelper(UIHelper):
    def __init__(self):
        super().__init__()  
    
    def load_neighbourhoods(self):
        return self.neighbourhoods_data.transform_neighbourhoods()
    
    def get_ward_options(self):
        neighbourhoods = self.load_neighbourhoods()
        return self.neighbourhoods_processes.sort_wards(neighbourhoods, 'name')
    
    def get_filtered_neighbourhood(self, option):
        neighbourhoods = self.load_neighbourhoods()
        return self.neighbourhoods_processes.filter_ward_by_option(neighbourhoods, option)
    
    def load_neighbourhood_overviews(self):
        return self.neighbourhoods_data.transform_neighbourhood_overviews()
    
    def get_filtered_neighbourhood_overviews(self, option):
        neighbourhood_overviews = self.load_neighbourhood_overviews()
        return self.neighbourhoods_processes.filter_neighbourhood_reviews_by_ward(neighbourhood_overviews, option)

    def get_neighbourhood_sentiment_metrics(self, option):
        filtered_neighbourhood_overview = self.get_filtered_neighbourhood_overviews(option)
        return self.neighbourhoods_processes.get_neighbourhood_sentiment_metrics(filtered_neighbourhood_overview)
    
    def get_global_neighbourhood_sentiment_metrics(self):
        neighbourhood_overviews = self.load_neighbourhood_overviews()
        return self.neighbourhoods_processes.get_neighbourhood_sentiment_metrics(neighbourhood_overviews)
    
    def get_neighbourhood_sentiment_deltas(self, option):
        filtered_sentiment_metrics = self.get_neighbourhood_sentiment_metrics(option)
        global_sentiment_metrics = self.get_global_neighbourhood_sentiment_metrics()

        overall_score_delta = filtered_sentiment_metrics['overall_score'] - global_sentiment_metrics['overall_score']
        positive_reviews_delta = filtered_sentiment_metrics['positive_reviews_percent'] - global_sentiment_metrics['positive_reviews_percent']
        negative_reviews_delta = filtered_sentiment_metrics['negative_reviews_percent'] - global_sentiment_metrics['negative_reviews_percent']
        neutral_reviews_delta = filtered_sentiment_metrics['neutral_reviews_percent'] - global_sentiment_metrics['neutral_reviews_percent']

        return {
            'overall_score_delta': overall_score_delta,
            'positive_reviews_percent_delta': positive_reviews_delta,
            'negative_reviews_percent_delta': negative_reviews_delta,
            'neutral_reviews_percent_delta': neutral_reviews_delta,
        }
    
    def show_neighbourhood_wordcloud(self, option):
        filtered_overviews = self.get_filtered_neighbourhood_overviews(option)
        wc = self.neighbourhoods_processes.make_neighbourhood_wordcloud(filtered_overviews)
        return wc