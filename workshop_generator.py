import requests
from bs4 import BeautifulSoup
from datetime import datetime
from sys import argv
import argparse

BASE_WORKSHOP_URL = "https://steamcommunity.com/sharedfiles/filedetails/?id="

RESOURCE_LINE     = 'resource.AddWorkshop("{}") -- {}\n'

HEADER =  '-- Auto-generated workshop file of collection {} ({})\n'
HEADER += '-- Generated on {}\n\n\n'


def get_header(title, url):
    header = HEADER.format(title, url, datetime.now())

    return header


def get_collection_url(workshop_id):
    url = "{}{}".format(BASE_WORKSHOP_URL, workshop_id)

    return url


def strip_url(url):
    stripped = url.replace(BASE_WORKSHOP_URL, '')

    return stripped


def get_site_content(url):
    print("Getting content of {}...".format(url))
    
    site_content = requests.get(url).text

    return site_content


def get_collection_items_from_soup(soup):
    collection_items = soup.find_all("div", {"class": "collectionItemDetails"})

    print("Found {} different collection items...".format(len(collection_items)))

    return collection_items


def get_workshop_title_from_soup(soup):
    workshop_title = soup.find("div", {"class": "workshopItemTitle"})

    return workshop_title.text


def get_link_tuples_from_collection_items(collection_items):
    link_tuples = []

    for item in collection_items:
        link_object = item.find("a", href=True)
    
        href = link_object['href']
        name = link_object.text

        print(name, '==>', href)

        link = strip_url(href)
    
        link_tuples.append( (link, link_object.text) )

    return link_tuples


def write_workshop_file(filename, header, link_tuples):
    try:
        f = open(filename, 'w')
        function_to_use = f.write
    except IOError:
        print("Failed to open file {} for writing... Defaulting to stdout!".format(filename))
        function_to_use = print

    function_to_use(header)

    for link_tuple in link_tuples:
        line = RESOURCE_LINE.format(link_tuple[0], link_tuple[1])

        function_to_use(line)

    if function_to_use != print:
        f.close()
       

def parse_args():
    parser = argparse.ArgumentParser(description='Generates workshop.lua files for GMod servers.')

    parser.add_argument('-o', '--output_dir', dest='output_directory',
                        help='The output directory to send the file to. Defaults to current working directory.',
                        default='.')
    parser.add_argument('-f', '--filename', dest='filename',
                        help='The filename to write to. Defaults to "workshop.lua".',
                        default='workshop.lua')
    parser.add_argument('-i', '--id', dest='collection_id',
                        help='The collection ID to replicate in the generated LUA file.',
                        default='1182709177')

    return parser.parse_args()
    


if __name__ == "__main__":

    args = parse_args()


    collection_url = get_collection_url(args.collection_id)

    site_content = get_site_content(collection_url)

    soup = BeautifulSoup(site_content, "html.parser")

    collection_items = get_collection_items_from_soup(soup)

    link_tuples = get_link_tuples_from_collection_items(collection_items)

    workshop_title = get_workshop_title_from_soup(soup)

    header = get_header(workshop_title, collection_url)

    filename = '{}/{}'.format(args.output_directory, args.filename)

    write_workshop_file(filename, header, link_tuples)

