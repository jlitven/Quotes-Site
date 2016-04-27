from flask import Flask, render_template, url_for, request
from flask_weasyprint import HTML, render_pdf
from flask_jsglue import JSGlue

#import my_quotes
# TODO: fix hack
import sys
from quotes_scraper import get_dictionary_quotes
from collections import defaultdict, Counter
import json

app = Flask(__name__)
jsglue = JSGlue(app)

def get_authors(quotes):
    quote_authors = [q['author'] for q in quotes]
    authors = []
    for author_name,_ in Counter(quote_authors).most_common():
        author_quotes = [q for q in quotes if q['author']==author_name]
        author_url = author_quotes[0]['author_url']
        image_url = author_quotes[0]['image_url']
        author = {
        'name': author_name,
        'quotes': [q['text'] for q in author_quotes],
        'author_url': author_url,
        'image_url': image_url
        }
        authors.append(author)
    return authors

def quotes_page(name="Joshua", user_id="27405185"):
    quotes = get_dictionary_quotes(user_id=user_id,
                                   num_quotes=1000,
                                   cached=False)
    authors = get_authors(quotes)
    return render_template("quotes.html",
                           title=name + "'s Quotes",
                           authors=authors)
@app.route('/quotes')
def quotes():
    return quotes_page()

@app.route('/single/<author>/<quote>/<font_family>')
def single(author, quote, font_family):
    return render_template("single.html",
                           author=author,
                           quote=quote,
                           font_family=font_family)

@app.route('/single_<author>_<quote>_<font_family>.pdf')
def single_pdf(author, quote, font_family):
    return render_pdf(url_for('single', author=author,
                              quote=quote, font_family=font_family))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_url_suffix = request.form['usr']
        [user_id, name] = username_url_suffix.split('-', 1)
        return quotes_page(name, user_id)
    else:
        return render_template("login.html")

if __name__ == '__main__':
    app.run(debug=True)
