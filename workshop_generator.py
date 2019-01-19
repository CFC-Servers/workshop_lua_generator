import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime


HTTP_OKAY = 200

BASE_WORKSHOP_URL = "https://steamcommunity.com/sharedfiles/filedetails/?id="

RESOURCE_LINE     = 'resource.AddWorkshop("{}") -- {}\n'

HEADER =  '-- Auto-generated workshop file of collection {} ({})\n'
HEADER += '-- Generated on {}\n\n\n'

QUIET_MODE = False

IS_MAIN = False


def die(string, code=0):
    print(string)
    exit(code)

def quiet_print(string):
    if QUIET_MODE or not IS_MAIN:
        return

    print(string)

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
    quiet_print("Getting content of {}...".format(url))
    
    response = requests.get(url)
    if response.status_code != HTTP_OKAY:
        die("ERROR! {} Did not return status code 200. Is the collection ID correct?".format(url))  

    site_content = response.text
    
    return site_content


def get_collection_items_from_soup(soup):
    collection_items = soup.find_all("div", {"class": "collectionItemDetails"})

    quiet_print("Found {} different collection items...".format(len(collection_items)))

    return collection_items


def get_workshop_title_from_soup(soup):
    workshop_title = soup.find("div", {"class": "workshopItemTitle"})

    return workshop_title.text


def get_link_tuples_from_collection_items(collection_items):
    link_tuples = []

    for i, item in enumerate(collection_items):
        link_object = item.find("a", href=True)
    
        href = link_object['href']
        name = link_object.text

        quiet_print("{}. {} ==> {}".format(i + 1, name, href))

        link = strip_url(href)
    
        link_tuples.append( (link, link_object.text) )

    return link_tuples


def write_workshop_file(filename, workshop_collection):
    try:
        f = open(filename, 'w')
        function_to_use = f.write
    except IOError:
        quiet_print("Failed to open file {} for writing... Defaulting to stdout!".format(filename))
        function_to_use = quiet_print

    header = get_header(workshop_collection['title'], workshop_collection['url'])
    
    function_to_use(header)

    for item in workshop_collection['items']:
        line = RESOURCE_LINE.format(item['id'], item['name'])

        function_to_use(line)

    if function_to_use != quiet_print:
        quiet_print('\nWorkshop file written to {}'.format(filename))
        f.write('\n')
        f.close()
       

def get_workshop_collection(collection_id):
    collection_url = get_collection_url(collection_id)

    site_content = get_site_content(collection_url)

    soup = BeautifulSoup(site_content, "html.parser")

    collection_items = get_collection_items_from_soup(soup)

    link_tuples = get_link_tuples_from_collection_items(collection_items)

    workshop_title = get_workshop_title_from_soup(soup)

    collection = {}
    collection['title'] = workshop_title
    collection['url']   = collection_url
    collection['items'] = []

    for link_tuple in link_tuples:
        item = {'id': link_tuple[0], 'name': link_tuple[1]}

        collection['items'].append(item)

    return collection



if __name__ == "__main__":
    IS_MAIN = True
    
    parser = argparse.ArgumentParser(description='Generates workshop.lua files for GMod servers.')
    
    parser.add_argument('-o', '--output_dir', dest='output_directory',
                        help='The output directory to send the file to. Defaults to current working directory.',
                        default='.')
    parser.add_argument('-f', '--filename', dest='filename',
                        help='The filename to write to. Defaults to "workshop.lua".',
                        default='workshop.lua')
    parser.add_argument('-i', '--id', dest='collection_id',
                        help="The collection ID to replicate in the generated LUA file. Defaults to my favorite server's collection",
                        default='1182709177')
    
    parser.add_argument('-q', '--quiet', dest='quiet_mode', help='Want this darn script to shutup (no output)? Set this flag!', action='store_true', default=False)

    args = parser.parse_args()


    QUIET_MODE = args.quiet_mode

    filename = '{}/{}'.format(args.output_directory, args.filename)

    workshop_collection = get_workshop_collection(args.collection_id)

    write_workshop_file(filename, workshop_collection)

