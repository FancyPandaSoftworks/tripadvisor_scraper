import numpy as np
import pandas as pd
from selenium import webdriver
import time
import constants as c

# ===
# Virtually going into the browser to prevent bot detection
# Get the HTML regardless of the main structure used by the website (e.g. Javascript website generation)
# ===


def scrape_tripadvisor(browser, main_link):

    browser.get(main_link)

    # ---
    # Scrape all the links that get the categories of tripadvisor
    # ---

    # Get all the hyperlinks that we sort by certain categories (fine dining, delivery available)
    href_links = browser.find_element_by_id('component_46').find_elements_by_class_name('erpDh')

    # Check whether the link contains these words, otherwise remove it
    # Modify the link such that we are able to use it directly, as some will just return to main page
    words = ['zfm', 'zfp', '?zfm', '?zfp']
    hyperlink_list = []
    for sub_link in href_links:
        if all(word not in sub_link.get_attribute('outerHTML') for word in words):
            continue
        elif '?' in sub_link.get_attribute('outerHTML'):
            continue
        else:
            link = sub_link.get_attribute('outerHTML').split('" ')[1].split('>')[0].split('href="')[1].split('"')[0]
            hyperlink_list.append(link)

    # ---
    # Scrape into the links, and get the restaurant information from the page
    # ---

    all_restau_info_list = []
    for sub_link in hyperlink_list:
        browser.get('https://www.tripadvisor.com/' + sub_link)

        all_restaurant_link = browser.find_elements_by_class_name('OhCyu')

        processed_restaurant_link = []

        # Retrieve all html links from the selenium object list
        for restau_link in all_restaurant_link:
            processed_restaurant_link.append(restau_link.get_attribute('outerHTML').split('href="')[1].split('" class')[0])

        # Go through every restaurant
        for link in processed_restaurant_link:
            browser.get('https://www.tripadvisor.com' + link)
            title = browser.find_element_by_class_name('fHibz').text

            # If there is more than one page to scrape, we need to go through the pages
            scrape_page = True
            while scrape_page:

                reviews = browser.find_elements_by_class_name('review-container')

                # Open the comments so we can get the entire text

                for review in reviews:

                    # Box containing all the info we need to scrape per review
                    review_box = review.find_element_by_class_name('is-9')

                    # ~~~
                    # All the review elements
                    # ~~~

                    # Score
                    review_score = int(
                        review_box.find_element_by_class_name('ui_bubble_rating').get_attribute('outerHTML').split('bubble_')[
                            2].split('0')[0])

                    # Comment
                    # Some comments are split due to the amount of text, so we need to merge it if need
                    review_text = review_box.find_element_by_class_name('partial_entry').text
                    review_additional_text = review_box.find_elements_by_class_name('postSnippet')
                    if len(review_additional_text) > 0:
                        review_text = review_text.split('...More')[0]

                        # Text is outside the boundary, so use innerHTML
                        review_text = review_text + ' ' + review_additional_text[0].get_attribute('innerHTML')

                    # Date
                    review_date = review_box.find_element_by_class_name('ratingDate').text.split('Reviewed ')[1]

                    # Name (Retrieved from another box)
                    review_name = review.find_element_by_class_name('is-2').find_element_by_class_name('info_text'). \
                        get_attribute('innerHTML').split('<div>')[1].split('</div>')[0]

                    # Store the information of the comment about the restaurant in a list
                    row_list = [title, review_name, review_date, review_score, review_text]
                    all_restau_info_list.append(row_list)

                try:
                    # For each page, scrape the comments
                    # As not all the pages are shown on 1 html page code, we need to click next until it is not possible
                    click_page = browser.find_element_by_class_name('ui_pagination').find_element_by_link_text('Next'). \
                        get_attribute('href')
                    browser.get(click_page)

                except:
                    scrape_page = False
    # ---
    # Transform the records into a dataframe
    # ---
    restaurant_review_df = pd.DataFrame.from_records(all_restau_info_list,
                                                     columns=['title', 'review_name', 'review_date', 'review_score',
                                                              'review_text'])

    restaurant_review_df.to_csv('data/restaurant_review.csv')