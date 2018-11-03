from flask import Flask
import base64
import cv2
import io
from imageio import imread

app = Flask(__name__)


@app.route('/make_new/<id>')
def hello_world(id):
    return '<img href="profile.png"></img>'

@app.route('/<id>')
def hello_world(id):
    return id



if __name__ == '__main__':
    app.run()

def get_parsed_data(img):
    """
    :param img: CV2 image that's BGR
    :return:
    """
