from flask import Flask, render_template
import base64
import cv2
import io
from imageio import imread

app = Flask(__name__)

output_text = ""

@app.route('/<id>')
def get_notes_page(id):
    if id[0:9] == "API_INPUT":
        img = get_image_from_sketch_back_end(id[9:])
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        output = get_parsed_data(img)
        make_file(output)
        save_file_to_sketch_back_end(id[9:])
        return render_template(id[9:] + ".html")
    else:
        get_file_from_sketch_back_end(id)
        return render_template(id + ".html")
TEMP = "temp.html"
def get_file_from_sketch_back_end(id):
    return None #TODO: get a file from back end
def get_image_from_sketch_back_end(id):
    return None #TODO: get an image from back end
def make_file(output):
    return "Hello, World!"
    header = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="">
    <meta name="author" content="">
    <title>Rohan Jhunjhunwala, Software Portfolio</title>
    <link rel="stylesheet" type="text/css" href="static/stylesheets/stylesheet.css" media="screen">
    <!-- Bootstrap core CSS -->
    <link href="static/vendor/bootstrap/css/bootstrap.min.css" rel="stylesheet">
    <!-- Custom fonts for this template -->
    <link href="https://fonts.googleapis.com/css?family=Saira+Extra+Condensed:500,700" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css?family=Muli:400,400i,800,800i" rel="stylesheet">
    <link href="static/vendor/fontawesome-free/css/all.min.css" rel="stylesheet">
    <!-- Custom styles for this template -->
    <link href="static/css/resume.css" rel="stylesheet">
    </head>
    <body>
    """
    if any(lst[0] == "HEAD" for lst in output):
        header+='<nav class="navbar navbar-expand-lg navbar-dark bg-primary fixed-top" id="sideNav">'
        header+="""
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <ul class="navbar-nav">
        """
        for lst in output:
            if lst[0] == "HEAD":
                header+= '<li class="nav-item">'
                header += '<a class="nav-link js-scroll-trigger" href="#%s">%s</a>' %(lst[0], lst[0])
                header+='</li>'

        header+="</ul></div></nav>"
    unclosed_head = False
    if unclosed_head:
        header+="</section>"
    header+="""
        <script src="../static/vendor/jquery/jquery.min.js"></script>
    <script src="../static/vendor/bootstrap/js/bootstrap.bundle.min.js"></script>
    <!-- Plugin JavaScript -->
    <script src="../static/vendor/jquery-easing/jquery.easing.min.js"></script>
    <!-- Custom scripts for this template -->
    <script src="../static/js/resume.min.js"></script>
    """
    header+="</body></html>"

    global output_text
    output_text = header
    return header #TODO: make a pretty HTML/CSS file... write it to temp
def save_file_to_sketch_back_end(id):
    f = open("templates/"+id+".html","w")
    f.write(output_text)
    f.close()
    return None #TODO: store the file in some persistent way.
def get_image_from_sketch_back_end():
    return None # TODO: get a file from sketchy back end
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
    # return 5
    return [["HEAD","Hello"],["IMAGE","../static/profile.png"],["TEXT", "This is a circuit"]]
