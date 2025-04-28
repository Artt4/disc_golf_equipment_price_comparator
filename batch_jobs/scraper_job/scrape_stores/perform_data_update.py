from scrape_stores.bulk_page_stucture.discking_scrape import get_data_discking
from scrape_stores.bulk_page_stucture.par3_scrape import get_data_par3
from scrape_stores.bulk_page_stucture.innovaeurope_scrape import get_data_discsport
from scrape_stores.bulk_page_stucture.diskiundiski_scrape import get_data_diskiundiskicesis
from scrape_stores.bulk_page_stucture.powergrip_scrape import get_data_powergrip_from_bulk
#from scrape_stores.single_page_structure.latitude64_scrape import run_latitude64_scraper


def run_all_scrapers():
    get_data_diskiundiskicesis() 
    get_data_discking() 
    get_data_discsport() 
    get_data_par3() 
    get_data_powergrip_from_bulk() 
    #run_latitude64_scraper()   Currently not working


