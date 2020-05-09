# A Helium function:
from helium import start_chrome, kill_browser


def test_home_page_load(client):
    driver = start_chrome(headless=True)
    print(driver.__dict__)
    # A Selenium API:
    # driver.execute_script("alert('Hi!');")
    kill_browser()
