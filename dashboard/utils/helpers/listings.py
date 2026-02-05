from .universal import UIHelper


# Listings helper functions
class ListingsHelper(UIHelper):
    def __init__(self, option=None):
        super().__init__()
        self.option = option

    def load_rated_listings(self):
        return self.listings_data.transform_listings_with_ratings()

    # Listings processing functions
    def get_data_table(self):
        rated_listings = self.load_rated_listings()
        return self.listings_processes.get_data_table(rated_listings)

    # Listings filtering function
    def get_filtered_listings(self):
        rated_listings = self.load_rated_listings()
        return self.listings_processes.filter_listings_by_ward(rated_listings, self.option)

    # Listings metrics function
    def get_listing_metrics(self):
        filtered_listings = self.get_filtered_listings()
        return self.listings_processes.get_metrics_for_ward_listings(filtered_listings)

    # Show sunburst chart in UI
    def show_tree_chart(self):
        filtered_listings = self.get_filtered_listings()
        return self.listings_processes.make_tree_chart(filtered_listings)
    
    # Global metrics for listings used in delta calculations
    def get_global_listing_metrics(self):
        rated_listings = self.load_rated_listings()
        return self.listings_processes.get_global_listing_metrics(rated_listings)
    
    # Delta calculations for listing metrics
    def get_listing_deltas(self):
        filtered_listing_metrics = self.get_listing_metrics()
        global_listing_metrics = self.get_global_listing_metrics()

        min_price_delta =  filtered_listing_metrics['min_price'] - global_listing_metrics['min_price']
        max_price_delta = filtered_listing_metrics['max_price'] - global_listing_metrics['max_price']
        average_price_delta =  filtered_listing_metrics['average_price'] - global_listing_metrics['average_price']
        average_rating_delta = filtered_listing_metrics['average_rating'] - global_listing_metrics['average_rating']
        average_occupancy_delta = filtered_listing_metrics['average_occupancy'] - global_listing_metrics['average_occupancy']
        average_revenue_delta = filtered_listing_metrics['average_revenue'] - global_listing_metrics['average_revenue']

        deltas = {
            'min_price_delta': min_price_delta,
            'max_price_delta': max_price_delta,
            'average_price_delta': average_price_delta,
            'average_rating_delta': average_rating_delta,
            'average_occupancy_delta': average_occupancy_delta,
            'average_revenue_delta': average_revenue_delta,
        }
        return deltas