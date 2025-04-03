print("Starting scraper service...")
import sys
import os

# Add the project root to Python's path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

try:
    print("Trying to import run_all_scrapers...")
    from app.scrape_stores.perform_data_update import run_all_scrapers
    print("Import successful.")

    print("About to run all scrapers...")
    run_all_scrapers()
except Exception as e:
    print("An error occurred:", e)
