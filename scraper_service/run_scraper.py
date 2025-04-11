print("Now starting scraper service...")
import sys
import os

# Go one level up from scraper_service to the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

try:
    print("Trying to import run_all_scrapers...")
    from scrape_stores.perform_data_update import run_all_scrapers
    print("Import successful.")

    print("About to run all scrapers...")
    run_all_scrapers()
except Exception as e:
    print("An error occurred:", e)