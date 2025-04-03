# scraper_service/run_scraper.py

import sys
import os

# Add the project root to Python's path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Now import your module
from app.scrape_stores.perform_data_update import run_all_scrapers

# Run the scrapers
run_all_scrapers()