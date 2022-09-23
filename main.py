### Ways to improve:
# Investigate the inclusion of items that are obtained through customization. Maybe this will throw some numbers off

### For reference:
#
# The two ways to write to a cell on Google Sheets:
#   hair_worksheet.update_cell(2, 3, 'Blue')
#   hair_worksheet.update('A2:B3', [["Gourds", "2"], ["Elegant Nobleman", "20"]])
#

# Imports for web scraping
import requests
from bs4 import BeautifulSoup
import re

# Imports for Google Sheets
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import pandas as pd

# Global variables
ARTICLE_TYPES = ['accessory', 'bottom', 'coat', 'dress', 'hair', 'hosiery', 'makeup', 'shoes', 'soul', 'top']

# Setup for web scraping
headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                           Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}

# Setup for Google Sheets
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
credentials = ServiceAccountCredentials.from_json_keyfile_name("google_sheets_key.json", scopes)
file = gspread.authorize(credentials)  # authenticate the JSON key with gspread
decompose_sheet = file.open("Decompose")  # open sheet

hair_worksheet = decompose_sheet.worksheet("Hair")
hair_worksheet.get_all_records()


def make_soup(item):
    base_url = "https://lovenikki.fandom.com/wiki/"
    item_name = item.replace('·', '-').replace(' ', '_')
    URL = base_url + item_name
    # print(URL)

    r = requests.get(url=URL, headers=headers)
    soup = BeautifulSoup(r.content, 'html5lib')
    return soup


def create_customization_dict(soup):
    print(item)
    soup_list = soup.prettify().splitlines()

    customization_dict = {}
    for line_count, line in enumerate(soup_list):
        if re.search("display:inline-block; width:40; height:40px; position:relative;", line):
            temp_line_count = line_count + 1
            while not re.search('a href="/wiki/', soup_list[temp_line_count]):
                temp_line_count = temp_line_count + 1
            customization_item = soup_list[temp_line_count].split('title="')[1].split('">')[0]
            customization_dict[customization_item] = 1

    return customization_dict


def create_crafting_dict(soup):
    crafting_table_lines = repr(
        soup.find('table', attrs={'class': 'article-table sortable tdc3 countrows-items'})).splitlines()

    crafting_dict = {}
    for count, line in enumerate(crafting_table_lines):
        if re.search('<td><a href=', line):
            article_name = line.split('title="')[1].split('">')[0].replace(' ', '_').replace('&amp;', '&')
            article_count = crafting_table_lines[count + 1].split('>')[1]

            crafting_dict[article_name] = article_count

    return crafting_dict


# This creates a dictionary of every article of clothing that an ingredient makes. Essentially it gives us the max
# number of one type of ingredient we'll ever need
def create_article_dictionary(item):
    # Get the list of articles that this ingredient crafts from the webpage
    soup = make_soup(item)

    customization_dict = create_customization_dict(soup)
    crafting_dict = create_crafting_dict(soup)

    articles_dict = customization_dict.copy()

    for article in crafting_dict:
        if re.search('\\(', article) and article.lower().split('(')[1].split(')')[0].strip() in ARTICLE_TYPES:
            article_to_add = article.split('(')[0].strip()
        else:
            article_to_add = article

        # print("Article to add: " + article_to_add + ", articles_dict.keys(): " + str(articles_dict.keys()))
        if article_to_add not in articles_dict.keys():
            articles_dict[article_to_add] = int(crafting_dict[article])
        else:
            articles_dict[article_to_add] = articles_dict[article] + crafting_dict[article]

    return articles_dict


# Remove all type_col from this function to make this return everything and not just hair
def get_list_of_owned_items(decomp=False):
    name = 1
    owned = 2
    type_col = 3
    decomposable = 22
    wardrobe_file = open("wardrobe_info.tsv", "r", encoding="utf8")

    return_list = []
    for line in wardrobe_file:
        split_line = line.split('\t')
        if split_line[owned] == "TRUE":
            if decomp:
                if split_line[decomposable] == "TRUE":
                    return_list.append(split_line[name].replace('·', '-'))
            else:
                return_list.append(split_line[name].replace('·', '-'))

    return return_list


def find_number_of_ingredient_needed(item, owned_items_list):
    articles_dict = create_article_dictionary(item)

    # print("Count for " + item + ":")
    number_of_ingredient_needed = 0
    for article in articles_dict:
        article_to_find_in_owned_list = article.replace('_', ' ').replace('&amp;', '&')
        if article_to_find_in_owned_list not in owned_items_list:
            number_of_ingredient_needed = number_of_ingredient_needed + int(articles_dict[article])
    #        print("   " + article, number_of_ingredient_needed)
    #    else:
    #        print("   " + article, '(owned)')
    # print()

    return number_of_ingredient_needed


if __name__ == '__main__':
    # Get every decomposable item that we own
    # For now, I'm only getting the hair
    owned_decomp_items_list = get_list_of_owned_items(decomp=True)
    owned_items_list = get_list_of_owned_items()

    for row_count, item in enumerate(owned_decomp_items_list):
        num = find_number_of_ingredient_needed(item, owned_items_list)
        # hair_worksheet.update_cell(2, 3, 'Blue')

        hair_worksheet.update('A2:B3', [["Gourds", "2"], ["Elegant Nobleman", "20"]])
        exit()

    # create_article_dictionary()
