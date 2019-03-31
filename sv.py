
from flask import (Flask, request, redirect, Response, url_for,
                   send_from_directory, jsonify, send_file,
                   render_template, flash, stream_with_context
                   )

app = Flask(__name__)

@app.route('/')
def home():
    q = request.args.get('q', None)
    if q:
        return render_template('rank.html')
    else:
        return render_template('home.html')


if __name__ == '__main__':
    app.run()
