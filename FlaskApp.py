


'''
Just so you don't forget in the future
all you have to do is run python flaskapp.py to get this running.  Nothing else . 

'''

# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, request, send_file, flash
import os

#Need to do this to fire up the app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))

#This allows every template to access the company name and doesn't need it to be recalled
@app.context_processor
def inject_company_name():
    return dict(company_name="Popeyes")

#This is the homepage
@app.route('/')
def home():
    #return render_template('gradient.html')
    main_blurb = 'Unlocking the value of your business'
    sub_blurb = 'Optimizing businesses'
    return render_template('home.html', 
                           main_blurb=main_blurb,
                           sub_blurb = sub_blurb)


#This is the homepage
@app.route('/automation')
def automation():
    #return render_template('gradient.html')
    automation_blurb = 'Automating the repetitive tasks so you can focus on delivering value'
    return render_template('automation.html', 
                           content_blurb = automation_blurb)


#This is the homepage
@app.route('/optimization')
def optimization():
    #return render_template('gradient.html')
    optimization_blurb = 'Optimizing your existing processes allowing you more time to serve your business'
    return render_template('optimization.html', 
                           content_blurb = optimization_blurb)


#This is the homepage
@app.route('/analysis')
def analysis():
    #return render_template('gradient.html')
    analysis_blurb = 'Demystifying data allowing you to make powerful choices'
    return render_template('analysis.html', 
                           content_blurb = analysis_blurb)




if __name__ == '__main__':
    app.run(debug=True)

