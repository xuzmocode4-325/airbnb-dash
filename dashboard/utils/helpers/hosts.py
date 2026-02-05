from .universal import UIHelper

# Hosts helper functions
class HostsHelper(UIHelper):
    def __init__(self, option, listings_info):
        super().__init__()
        self.option = option
        self.listings_info = listings_info

    # Loads uniqe host dataframe
    def load_hosts(self):
        return self.host_data.transform_hosts()
   
    # Hosts processing functions
    def get_filtered_hosts(self):
        hosts = self.load_hosts()
        return self.host_processes.filter_hosts_by_ward(hosts, self.listings_info, self.option)

    # Hosts metrics function
    def get_filtered_host_metrics(self):
        filtered_hosts = self.get_filtered_hosts()
        return self.host_processes.get_metrics_for_ward_hosts(filtered_hosts)

    # Gets global host metrics for delta calculations
    def get_global_host_metrics(self):
        hosts = self.load_hosts()
        return self.host_processes.get_global_host_metrics(hosts)
    
    # Calculates deltas for currently selected ward
    def get_host_deltas(self):
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