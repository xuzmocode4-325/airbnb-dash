from .universal import DashboardProcesses


class HostsProcesses(DashboardProcesses):
    def __init__(self):
        super().__init__()

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