from flask import Flask

app = Flask(__name__)


@app.route('/<id>')
def hello_world(id):
    return id


if __name__ == '__main__':
    app.run()

def get_black_box(img):
    """

    :param img: the
    :return:
    """