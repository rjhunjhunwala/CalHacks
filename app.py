from flask import Flask

app = Flask(__name__)


@app.route('/?<id>')
def hello_world(g):
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
