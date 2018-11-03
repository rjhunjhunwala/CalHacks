from flask import Flask, render_template
# import base64
# import cv2
# import io
# from imageio import imread

app = Flask(__name__, static_url_path='')

@app.route('/make_new/<id>')
def make_new(id):
    return app.send_static_file("index.html")

@app.route('/<id>')
def get_notes_page(id):
    return render_template("index.html")

if __name__ == '__main__':
    app.run()

def get_parsed_data(img):
    """
    :param img: CV2 image that's BGR
    :return:
    """
