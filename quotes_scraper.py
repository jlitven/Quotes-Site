
'''
Goodreads Quotes Scraper.

Creates quotes from a Goodreads user name.

Joshua Litven 2016
'''
import sys
import requests
import os.path
import re
from bs4 import BeautifulSoup
import pdb
import pprint
import imp
import types

class Quote(object):
    '''
    Stores the quote data.
    '''
    def __init__(self, text, url, author, author_url, image_url):
        self.text = text
        self.url = url
        self.author = author
        self.author_url = author_url
        self.image_url = image_url

    def __str__(self):
        s = u'{}\n- {}'.format(self.text, self.author)
        return s.encode('utf-8')

    def __repr__(self):
        return self.__str__()

    def to_dictionary(self):
        d = {}
        d['text'] = self.text
        d['url'] = self.url
        d['author'] = self.author
        d['author_url'] = self.author_url
        d['image_url'] = self.image_url
        return d

# TODO: Fix Shaupernhaer quote
def create_quotes(url):

    res = requests.get(url = url)
    res.raise_for_status()
    content = res.content

    soup = BeautifulSoup(content, "lxml")

    for e in soup.findAll('br'):
        e.extract()

    quotes_text = soup.findAll('div', attrs={'class':'quoteText'})

    quotes_footer = soup.findAll('div', attrs={'class':'right'})

    quotes = []

    for (quote_text,f) in zip(quotes_text, quotes_footer):
        text = ''
        for e in quote_text.contents:
            if isinstance(e, basestring):
                text += e.strip() + '\n'
            else:
                break
        text = re.sub(u"  +", u"", text)
        text = text.replace(u'\n\u2015\n',u'')
        quote_link = quote_text.find('a')
        author_url = quote_link.get('href')
        author = quote_link.getText()
        footer_link = f.find('a')
        quote_url = footer_link.get('href')
        try:
            image_url = quote_text.parent.find('a').find('img').get('src')
            image_url = image_url.replace('p2', 'p4')
        except:
            image_url = ''
        quote = Quote(text, quote_url, author, author_url, image_url)
        quotes.append(quote)

    return quotes

def gen_goodreads_quote_pages(user_id):
    url = "https://www.goodreads.com/quotes/list/{}".format(str(user_id))
    yield url
    page = 2
    while True:
        yield url + '?page=' + str(page)
        page +=1

def get_quotes(user_id='27405185', num_quotes=100):
    print 'Scraping Goodread for quotes...'
    quotes = []
    for page in gen_goodreads_quote_pages(user_id):
        page_quotes = create_quotes(page)
        if page_quotes:
            quotes.extend(page_quotes)
            if len(quotes) > num_quotes:
                quotes = quotes[:num_quotes]
                break
        else:
            break
    return quotes

def get_data_dir():
    dir_name = 'quotes'
    path = os.getenv("HOME")
    dir_path = os.path.join(path, dir_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path

def get_quotes_file():
    dir_name = get_data_dir()
    return os.path.join(dir_name, 'my_quotes.py')

def get_dictionary_quotes(user_id='27405185',
                          num_quotes=100,
                          cached=True):

    if cached:
        scrape = False
        try:
            module = imp.load_source('my_quotes', get_quotes_file())
            dict_quotes = module.quotes
        except:
            print 'Cannot find cached quotes!'
            scrape = True
    else:
        scrape = True

    if scrape:
        quotes = get_quotes(user_id, num_quotes)
        dict_quotes = [quote.to_dictionary() for quote in quotes]
        with open(get_quotes_file(), 'w') as f:
            f.write('quotes = ' + pprint.pformat(dict_quotes) + '\n')

    return dict_quotes

def main():

    if len(sys.argv) > 1:
        quotes = get_quotes(sys.argv[1])
    else:
        quotes = get_quotes()

    for quote in quotes:
        print quote.to_dictionary()

if __name__ == '__main__':
    main()
