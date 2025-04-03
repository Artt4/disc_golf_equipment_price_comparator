from app.scrape_stores.bulk_page_stucture.discking_scrape import get_data_discking
from app.scrape_stores.bulk_page_stucture.par3_scrape import get_data_par3
from app.scrape_stores.bulk_page_stucture.innovaeurope_scrape import get_data_discsport
from app.scrape_stores.bulk_page_stucture.diskiundiski_scrape import get_data_diskiundiskicesis
from app.scrape_stores.bulk_page_stucture.powergrip_scrape import get_data_powergrip_from_bulk
from app.scrape_stores.single_page_structure.latitude64_scrape import get_all_pages_latitude64, get_data_latitude64



def run_all_scrapers():
    print("starting get_data_diskiundiskicesis")
    get_data_diskiundiskicesis() 
    print("starting get_data_discking")
    get_data_discking() 
    get_data_discsport() 
    get_data_par3() 
    get_data_powergrip_from_bulk() 

    all_urls_latitude64 = get_all_pages_latitude64()
    get_data_latitude64(all_urls_latitude64)

