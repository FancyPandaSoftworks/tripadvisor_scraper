import scraper
import constants as c


def run():
    scraper.scrape_tripadvisor(c.browser, c.main_link)


if __name__ == '__main__':
    run()