from flask import Flask, request, redirect, render_template

app = Flask(__name__)


@app.route('/hello', methods=['GET'])
def hello_world():
    return "Welcome to the service!"


def generate_short_url():
    import random
    import string
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for i in range(6))
    return short_url


url_mapping = {}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        long_url = request.form['long_url']
        short_url = generate_short_url()
        url_mapping[short_url] = long_url
        return render_template('index.html', short_url=f'{request.host_url}{short_url}')
    return render_template('index.html', short_url=None)


@app.route('/<short_url>')
def redirect_to_long_url(short_url):
    if short_url in url_mapping:
        long_url = url_mapping[short_url]
        return redirect(long_url)
    else:
        return "URL not found", 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
