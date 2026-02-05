import streamlit as st
from utils.dataloaders.hosts import HostsDataLoader
from utils.dataloaders.listings import ListingsDataLoader
from utils.dataloaders.neighbourhoods import NeighbourhoodsDataLoader

from utils.processes.hosts import HostsProcesses
from utils.processes.listings import ListingsProcesses
from utils.processes.neighbourhood import NeighbourhoodsProcesses


host_data = HostsDataLoader()
listings_data = ListingsDataLoader()
neighbourhoods_data = NeighbourhoodsDataLoader()

host_processes = HostsProcesses()
listings_processes = ListingsProcesses()
neighbourhoods_processes = NeighbourhoodsProcesses()

# Neighbourhoods helper functions

class UIHelper:
    def __init__(self):
        self.host_data = host_data
        self.host_processes = host_processes
        self.listings_data = listings_data
        self.listings_processes = listings_processes
        self.neighbourhoods_data = neighbourhoods_data
        self.neighbourhoods_processes = neighbourhoods_processes

     







   