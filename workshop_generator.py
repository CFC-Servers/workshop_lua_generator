import requests
import os
from bs4 import BeautifulSoup
from datetime import datetime


class WorkshopGeneratorError(Exception):
    pass

class NoWorkshopID(WorkshopGeneratorError):
    pass

class InvalidWorkshopID(WorkshopGeneratorError):
    pass

class NoCollection(WorkshopGeneratorError):
    pass


class WorkshopGenerator():
    HTTP_OKAY = 200

    BASE_WORKSHOP_URL = "https://steamcommunity.com/sharedfiles/filedetails/?id="

    RESOURCE_LINE     = 'resource.AddWorkshop("{}") -- {}\n'

    HEADER =  '-- Auto-generated workshop file of collection {} ({})\n'
    HEADER += '-- Generated on {}\n\n\n'
    
    DEFAULT_FILENAME = 'workshop.lua'

    def __init__(self, collection_id=None, output_directory='', filename='', suppress_output=True):
        self.collection_id = collection_id

        self.output_dir = output_directory

        self.filename = filename if filename else self.DEFAULT_FILENAME

        self.quiet_mode = suppress_output

        self.collection = None

    def configure(self, filename='', collection_id='', suppress_output=None, output_directory=''):
        if filename:
            self.filename = filename
        if collection_id:
            self.collection_id = collection_id
        if supress_output:
            self.quiet_mode = supress_output
        if output_directory:
            self.output_directory = output_directory

    def set_filename(self, filename):
        self.filename = filename

    def set_output_dir(self, output_dir):
        self.output_dir = output_dir

    def set_collection_id(self, collection_id):
        self.collection_id = collection_id

    def set_quiet_mode_enabled(self, quiet_mode_enabled):
        self.quiet_mode = quiet_mode_enabled

    def _quiet_print(self, string):
        if self.quiet_mode:
            return
    
        print(string)


    def _get_header(self, title, url):
        header = self.HEADER.format(title, url, datetime.now())

        return header


    def _get_collection_url(self, workshop_id):
        url = "{}{}".format(self.BASE_WORKSHOP_URL, workshop_id)

        return url


    def _strip_url(self, url):
        stripped = url.replace(self.BASE_WORKSHOP_URL, '')

        return stripped


    def _get_site_content(self, url):
        self._quiet_print("Getting content of {}...".format(url))
    
        response = requests.get(url)
        if response.status_code != self.HTTP_OKAY:
            raise ConnectionError("{} Did not return status code 200. Is the collection ID correct?".format(url))

        site_content = response.text

        # Not a collection if this isn't in the page contents
        if not 'subscribeCollection' in site_content:
            raise InvalidWorkshopID()
    
        return site_content


    def _get_collection_items_from_soup(self, soup):
        collection_items = soup.find_all("div", {"class": "collectionItemDetails"})

        self._quiet_print("Found {} different collection items...".format(len(collection_items)))
    
        return collection_items


    def _get_workshop_title_from_soup(self, soup):
        workshop_title = soup.find("div", {"class": "workshopItemTitle"})

        return workshop_title.text


    def _get_link_tuples_from_collection_items(self, collection_items):
        link_tuples = []

        for i, item in enumerate(collection_items):
            link_object = item.find("a", href=True)
    
            href = link_object['href']
            name = link_object.text

            self._quiet_print("{}. {} ==> {}".format(i + 1, name, href))

            link = self._strip_url(href)
    
            link_tuples.append( (link, link_object.text) )

        return link_tuples


    def write_workshop_file(self, workshop_collection = None, filename = None, output_dir = None):
        if workshop_collection == None:
            if self._collection_id_set():
                workshop_collection = self.get_workshop_collection()
            else:
                raise NoCollection()

        if filename == None:
            filename = self.filename

        if output_dir == None:
            output_dir = self.output_dir

        file_path = '{}{}{}'.format(output_dir, os.sep, filename) if output_dir else filename

        f = open(file_path, 'w')
        function_to_use = f.write
        
        header = self._get_header(workshop_collection['title'], workshop_collection['url'])
    
        function_to_use(header)

        for item in workshop_collection['items']:
            line = self.RESOURCE_LINE.format(item['id'], item['name'])

            function_to_use(line)

        self._quiet_print('\nWorkshop file written to {}'.format(file_path))
        f.write('\n')
        f.close()
 

    def _collection_id_set(self):
        if self.collection_id:
            return True

        return False

    def get_workshop_collection(self, collection_id = None):
        if collection_id == None:
            if self._collection_id_set():
                collection_id = self.collection_id
            else:
                raise NoWorkshopID()
        else:
            self.collection_id = collection_id

        collection_url = self._get_collection_url(collection_id)

        site_content = self._get_site_content(collection_url)

        soup = BeautifulSoup(site_content, "html.parser")

        collection_items = self._get_collection_items_from_soup(soup)

        link_tuples = self._get_link_tuples_from_collection_items(collection_items)

        workshop_title = self._get_workshop_title_from_soup(soup)

        collection = {}
        collection['title'] = workshop_title
        collection['url']   = collection_url
        collection['items'] = []

        for link_tuple in link_tuples:
            item = {'id': link_tuple[0], 'name': link_tuple[1]}

            collection['items'].append(item)

        self.collection = collection

        return collection



if __name__ == "__main__":
    import argparse
    
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

    wg = WorkshopGenerator(filename=args.filename, output_directory=args.output_directory, collection_id=args.collection_id, suppress_output=args.quiet_mode)

    wg.write_workshop_file()

