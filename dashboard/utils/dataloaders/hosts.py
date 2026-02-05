from .universal import LoadNormalisedData

class HostsDataLoader(LoadNormalisedData):
    def __init__(self):
        super().__init__()  
    
    def transform_hosts(self):
        """Clean and deduplicate hosts data."""
        drop_cols = [
            'host_name', 'host_location', 
            'host_has_profile_pic', 'host_about', 'host_verifications'   
        ]
        
        # Only drop columns that actually exist
        existing_drop_cols = [col for col in drop_cols if col in self.hosts.columns]
        hosts_cleaned = self.hosts.drop(columns=existing_drop_cols)
        
        # Deduplicate and reset index
        hosts_cleaned = hosts_cleaned.drop_duplicates(subset=['host_id']).reset_index(drop=True)

        return hosts_cleaned