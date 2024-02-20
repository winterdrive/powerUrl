from flask import Flask, request, redirect
import string
import random

app = Flask(__name__)
url_mapping = {}


@app.route('/hello-world', methods=['GET'])
def hello_world():
    return "Wellcome to the service!"


def generate_short_url():
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for i in range(6))
    return short_url


@app.route('/shorten', methods=['POST'])
def shorten_url():
    long_url = request.form['long_url']
    short_url = generate_short_url()
    url_mapping[short_url] = long_url
    return f'Shortened URL: {request.host_url}{short_url}'


@app.route('/<short_url>')
def redirect_to_long_url(short_url):
    if short_url in url_mapping:
        long_url = url_mapping[short_url]
        return redirect(long_url)
    else:
        return "URL not found", 404


if __name__ == '__main__':
    app.run(debug=True)