from selenium import webdriver


# ---
# Get the constants variables that won't change over time
# Browser: The virtual environment we are going to use to scrape data
# main_link: Place to start the scraping
# ---
browser = webdriver.Chrome(executable_path=r'chromedriver/chromedriver.exe')
main_link = 'https://www.tripadvisor.com/Restaurants-g188632-Rotterdam_South_Holland_Province.html'