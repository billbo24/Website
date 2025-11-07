


'''
Just so you don't forget in the future
all you have to do is run python flaskapp.py to get this running.  Nothing else . 

'''

# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, request, send_file, flash
from helper import to_uppercase
import PDF_Reader
import io
from openpyxl import Workbook, load_workbook
from scraper_service import process_pdfs
import os

#Need to do this to fire up the app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))

#This is the homepage
@app.route('/')
def landing():
    #return render_template('gradient.html')
    return render_template('home.html')



if __name__ == '__main__':
    app.run(debug=True)

