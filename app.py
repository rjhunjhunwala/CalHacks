from flask import Flask
# import base64
# import cv2
# import io
# from imageio import imread

app = Flask(__name__)
app.static_url_path = "/static"
app.send_static_file("/static/profile.png")

@app.route('/make_new/<id>')
def make_new(id):
    return '<img src="profile"></img>'

@app.route('/<id>')
def get_notes_page(id):
    return id

if __name__ == '__main__':
    app.run()

def get_parsed_data(img):
    """
    :param img: CV2 image that's BGR
    :return:
    """
