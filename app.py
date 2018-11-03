from flask import Flask, render_template
import base64
import cv2
import io
from imageio import imread

app = Flask(__name__)

@app.route('/make_new/<id>')
def make_new(id):
    return app.send_static_file("index.html")

@app.route('/<id>')
def get_notes_page(id):
    return render_template("index.html")

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response
if __name__ == '__main__':
    app.run()

def get_parsed_data(img):
    """
    :param img: CV2 image that's BGR
    :return:
    """
