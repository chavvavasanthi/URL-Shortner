from flask import Flask, request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
import random
import string
import os

# Flask App
app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database
db = SQLAlchemy(app)


# Database Model
class Urls(db.Model):

    id_ = db.Column("id_", db.Integer, primary_key=True)
    long = db.Column("long", db.String())
    short = db.Column("short", db.String(10))

    def __init__(self, long, short):
        self.long = long
        self.short = short


# Create Database Tables
with app.app_context():
    db.create_all()


# Function to Generate Short URL
def shorten_url():

    letters = string.ascii_lowercase + string.ascii_uppercase

    while True:

        random_letters = random.choices(letters, k=3)

        random_string = "".join(random_letters)

        existing_url = Urls.query.filter_by(short=random_string).first()

        if not existing_url:
            return random_string


# Home Route
@app.route('/', methods=['GET', 'POST'])
def home():

    if request.method == "POST":

        url_received = request.form["nm"]

        found_url = Urls.query.filter_by(long=url_received).first()

        # If URL already exists
        if found_url:

            return redirect(
                url_for(
                    "display_short_url",
                    url=found_url.short
                )
            )

        # Create New Short URL
        else:

            short_url = shorten_url()

            new_url = Urls(url_received, short_url)

            db.session.add(new_url)

            db.session.commit()

            return redirect(
                url_for(
                    "display_short_url",
                    url=short_url
                )
            )

    else:
        return render_template('url_page.html')


# Redirect to Original URL
@app.route('/<short_url>')
def redirection(short_url):

    long_url = Urls.query.filter_by(short=short_url).first()

    if long_url:
        return redirect(long_url.long)

    else:
        return "<h1>URL does not exist</h1>"


# Display Short URL
@app.route('/display/<url>')
def display_short_url(url):

    full_short_url = request.url_root.rstrip('/') + '/' + url

    return render_template(
        'shorturl.html',
        short_url_display=url,
        full_short_url=full_short_url
    )


# Display All URLs
@app.route('/all_urls')
def display_all():

    return render_template(
        'all_urls.html',
        vals=Urls.query.all()
    )


# Run Flask App
if __name__ == '__main__':
    app.run(port=5000, debug=True)