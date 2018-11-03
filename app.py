from flask import Flask
import base64
import cv2
import io
from imageio import imread

app = Flask(__name__)


@app.route('/make_new/<id>')
def hello_world(id):
    image = get_parsed_data(imread(io.BytesIO(base64.b64decode(id))))
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.imwrite("last_image",image)
    return '<img href="last_image"></img>'

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
