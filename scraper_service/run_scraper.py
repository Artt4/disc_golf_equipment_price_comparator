print("Now starting scraper service...")
import sys
import os

# Go one level up from scraper_service to the project root
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

#docker build -t run-scraper -f scraper_service/Dockerfile .
#docker build --no-cache -t run-scraper -f scraper_service/Dockerfile .
    
#docker run --env-file .env run-scraper
#docker run -it --env-file .env run-scraper bash

#docker run -p 8080:8080 discgolf-app
#docker build -t discgolf-app .