from flask import Flask, render_template, request, redirect, url_for
from main import run_scrapping
from comparison import run_comparison_script
import re

app = Flask(__name__)
app.secret_key = "3ab2b6570b61a85a3df8be9d63dfdaab"

cached_results = []  # Temporary global variable

def extract_price(p):
    try:
        return float(re.sub(r'[^\d.]', '', str(p)))
    except:
        return 0.0

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/track', methods=['GET', 'POST'])
def track():
    if request.method=='POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        prod_link = request.form['prod_link']
        desirable_price = int(request.form['desirable_price'])
        phone_no = request.form['phone_no']
        
        print(f"First Name: {first_name}, Last Name: {last_name}, Product Link: {prod_link}, Desirable Price: {desirable_price}, Phone No: {phone_no}")

        result = run_comparison_script(prod_link, desirable_price, phone_no, first_name, last_name)
        
        return result
    return render_template('track.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    global cached_results

    per_page = 10
    page = request.args.get('page', 1, type=int)
    sort_order = request.args.get('sort_order', 'none')

    if request.method == 'POST':
        prod_name = request.form.get('prod_name')
        min_price = request.form.get('min_price')
        max_price = request.form.get('max_price')
        sort_order = request.form.get('sort_order', 'none')

        if not prod_name or not min_price or not max_price:
            message = "Please fill in all the fields: Product Name, Minimum Price, and Maximum Price."
            return render_template('search.html', message=message)

        cached_results = run_scrapping(prod_name, min_price, max_price)

        if cached_results == "gibberish_search":
            return render_template('search.html', error="Products searched not found", searched=True)

        if isinstance(cached_results, str):
            return render_template('search.html', message=cached_results, searched=True)

        if sort_order == "asc":
            cached_results.sort(key=lambda x: extract_price(x['price']))
        elif sort_order == "desc":
            cached_results.sort(key=lambda x: extract_price(x['price']), reverse=True)

        total = len(cached_results)
        paginated = cached_results[(page - 1) * per_page: page * per_page]

        return render_template('search.html', results=paginated, searched=True, sort_order=sort_order, page=page, total_pages=(total + per_page - 1) // per_page)

    if cached_results:
        if sort_order == "asc":
            cached_results.sort(key=lambda x: extract_price(x['price']))
        elif sort_order == "desc":
            cached_results.sort(key=lambda x: extract_price(x['price']), reverse=True)

        total = len(cached_results)
        paginated = cached_results[(page - 1) * per_page: page * per_page]
        return render_template('search.html', results=paginated, searched=True, sort_order=sort_order, page=page, total_pages=(total + per_page - 1) // per_page)

    return render_template('search.html', searched=False, results=None, sort_order="none", page=1, total_pages=0)
