import re
import pandas as pd


class DashboardProcesses:
    """Utility class for dashboard data processing and filtering operations."""
    def __init__(self):
        pass

    def _extract_num(self, ward):
        """Extract numeric ID from ward name string.
        
        Args:
            ward: str, ward name in format 'Ward {num}'
            
        Returns:
            int: ward number or float('inf') if no match found
        """
        match = re.search(r'Ward (\d+)', ward)
        return int(match.group(1)) if match else float('inf') 

    
