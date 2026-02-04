import streamlit as st
from utils.dataloader import TransformedData
from utils.processes import DashboardProcesses

data = TransformedData()
processes = DashboardProcesses()


# Neighbourhoods helper functions

class UIHelper:
    def __init__(self):
        self.data = TransformedData()
        self.processes = DashboardProcesses()

class NeighbourhoodsHelper(UIHelper):
    def __init__(self):
        super().__init__()  
    
    def load_neighbourhoods(_self):
        return _self.data.transform_neighbourhoods()
    
    def get_ward_options(self):
        neighbourhoods = self.load_neighbourhoods()
        return self.processes.sort_wards(neighbourhoods, 'name')
    
    def get_filtered_neighbourhood(self, option):
        neighbourhoods = self.load_neighbourhoods()
        return self.processes.filter_ward_by_option(neighbourhoods, option)

# Listings helper functions
class ListingsHelper(UIHelper):
    def __init__(self, option=None):
        super().__init__()
        self.option = option

    def load_rated_listings(self):
        return self.data.transform_listings_with_ratings()

    # Listings processing functions
    def get_data_table(self):
        rated_listings = self.load_rated_listings()
        return self.processes.get_data_table(rated_listings)

    # Listings filtering function
    def get_filtered_listings(self):
        rated_listings = self.load_rated_listings()
        return self.processes.filter_listings_by_ward(rated_listings, self.option)

    # Listings metrics function
    def get_listing_metrics(self):
        filtered_listings = self.get_filtered_listings()
        return self.processes.get_metrics_for_ward_listings(filtered_listings)
    
    def get_global_listing_metrics(self):
        rated_listings = self.load_rated_listings()
        return self.processes.get_global_listing_metrics(rated_listings)
    
    def get_listing_metrics_deltas(self):
        filtered_listing_metrics = self.get_listing_metrics()
        global_listing_metrics = self.get_global_listing_metrics()

        delta_min_price =  filtered_listing_metrics['min_price'] - global_listing_metrics['min_price']
        delta_max_price = filtered_listing_metrics['max_price'] - global_listing_metrics['max_price']
        delta_average_price =  filtered_listing_metrics['average_price'] - global_listing_metrics['average_price']
        delta_average_rating = filtered_listing_metrics['average_rating'] - global_listing_metrics['average_rating']
        
        deltas = {
            'min_price_delta': delta_min_price,
            'max_price_delta': delta_max_price,
            'average_price_delta': delta_average_price,
            'average_rating_delta': delta_average_rating,
        }
        return deltas

# Hosts helper functions
class HostsHelper(UIHelper):
    def __init__(self, option, listings_info):
        super().__init__()
        self.option = option
        self.listings_info = listings_info

    def load_hosts(self):
        return self.data.transform_hosts()
   
    # Hosts processing functions
    def get_filtered_hosts(self):
        hosts = self.load_hosts()
        return self.processes.filter_hosts_by_ward(hosts, self.listings_info, self.option)

    # Hosts metrics function
    def get_filtered_host_metrics(self):
        filtered_hosts = self.get_filtered_hosts()
        return self.processes.get_metrics_for_ward_hosts(filtered_hosts)

    def get_global_host_metrics(self):
        hosts = self.load_hosts()
        return self.processes.get_global_host_metrics(hosts)
    
    def get_host_metrics_deltas(self):
        filtered_hosts_metrics = self.get_filtered_host_metrics()
        global_host_metrics = self.get_global_host_metrics()

        delta_mean_response_rate = filtered_hosts_metrics['mean_response_rate'] - global_host_metrics['mean_response_rate']
        delta_mean_acceptance_rate = filtered_hosts_metrics['mean_acceptance_rate'] - global_host_metrics['mean_acceptance_rate']
        delta_verified_hosts_percent = filtered_hosts_metrics['verified_hosts_percent'] - global_host_metrics['verified_hosts_percent']
        delta_super_hosts_percent = filtered_hosts_metrics['super_hosts_percent'] - global_host_metrics['super_hosts_percent']      
        
        deltas = {
            'mean_response_rate_delta': delta_mean_response_rate,
            'mean_acceptance_rate_delta': delta_mean_acceptance_rate,
            'verified_hosts_percent_delta': delta_verified_hosts_percent,
            'super_hosts_percent_delta': delta_super_hosts_percent,
        }
        return deltas