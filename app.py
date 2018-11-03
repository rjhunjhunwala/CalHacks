from flask import Flask

app = Flask(__name__)


@app.route('/<id>')
def hello_world(id):
    return 'Hello World!' + id


if __name__ == '__main__':
    app.run()
