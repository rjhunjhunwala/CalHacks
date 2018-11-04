from flask import Flask, render_template, render_template_string
import cv2
import io
from imageio import imread
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from four_point_transform import four_point_transform

from apiclient import errors
from apiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
import tensorflow as tf
import keras
from skimage.filters import threshold_local
from PIL import Image, ImageOps, ImageDraw
from scipy.ndimage import morphology, label
import pytesseract
from wrapper import *
from random import randint
import numpy as np
import scipy
import pickle
import imutils

import wrapper

app = Flask(__name__)

output_text = ""

@app.route('/<id>')
def get_notes_page(id):
    if id[0:9] == "API_INPUT":
        img = wrapper.getCV2_from_file(id[9:]+".jpg")
        output = get_parsed_data(img)
        output_string = make_file(output)
        store_string_back_end(id[9:], output_string)
        return render_template_string(output_string)
    else:
        return render_template_string(get_string_from_sketch_back_end(id))
TEMP = "temp.html"
def get_string_from_sketch_back_end(id):
    return wrapper.get_string_from_file(id+".txt")
def store_string_back_end(id, string):
    fil = open(id + ".txt", "w")
    fil.write(string)
    fil.close()
    wrapper.upload_file(id+".txt")

def make_file(output):
    header = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="">
    <meta name="author" content="">
    <title>Cal Hacks, Notes to Web</title>
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
                header += '<a class="nav-link js-scroll-trigger" href="#%s">%s</a>' %(lst[1], lst[1])
                header+='</li>'
        header+="</ul></div></nav>"

    unclosed_head = False

    for lst in output:
        if lst[0] == "HEAD":
            if unclosed_head:
                header+='</div><hr class="m-0"></section>'
            unclosed_head = True
            header+='<section class="resume-section p-3 p-lg-5 d-flex flex-column" id="%s"><div class="my-auto">' %lst[1]
            header+='<h1>'+lst[1]+"</h1>"
        elif lst[0] == "IMAGE":
            header += '<div class ="section-gallery container">'
            for lstT in lst[1]:
                header +='<a class="elem-gallery" style="background-image: url(\'%s\')" title="3D Engine">'%(lstT)+'</a>'
            header += '</div>'
        else: #paragraph
            header+='<p>' + lst[1] + '</p>'



    if unclosed_head:
        header += '</div><hr class="m-0"></section>'

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
def get_image_from_sketch_back_end(id):
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
    app.run(debug=True)



def get_parsed_data(img):
    """
    :param img: CV2 image that's BGR
    :return:
    """
    ratio = img.shape[0]/500.0
    orig = img.copy()
    img = imutils.resize(img, height=500)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5,5), 0)
    def autocanny(image, sigma=0.33):
        v = np.median(image)
        lower = int(max(0, (1.0-sigma)*v))
        upper = int(min(255, (1.0+sigma)*v))
        edged = cv2.Canny(image, lower, upper)
        return edged
    edged = autocanny(gray)
    cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02*peri, True)
        if len(approx)==4:
            screenCnt = approx
            break
    warped = four_point_transform(orig, screenCnt.reshape(4,2)*ratio)
    warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    T = threshold_local(warped, 11, offset=10, method="gaussian")
    warped = (warped>T).astype("uint8")*255
    height, width = warped.shape
    warped = warped[int(0.05*height): int(0.95*height), int(0.01*width): int(0.99*width)]
    gray = cv2.GaussianBlur(warped, (5,5), 0)
    edged = autocanny(gray)
    warped = cv2.cvtColor(warped,cv2.COLOR_GRAY2RGB)
    kernel = np.ones((3,3),np.uint8)
    edged = cv2.dilate(edged, kernel, iterations=1)
    cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    pil_im = Image.fromarray(warped)
    class Line():
        box=False
        def __init__(self, coordinates):
            self.coordinates = coordinates
    class Box():
        box=True
        def __init__(self, coordinates):
            self.coordinates = coordinates
    def boxes(orig):
        img = ImageOps.grayscale(orig)
        im = np.array(img)
        
        # Inner morphological gradient.
        im = morphology.grey_dilation(im, (3, 3)) - im
        
        # Binarize.
        mean, std = im.mean(), im.std()
        t = mean + std
        im[im < t] = 0
        im[im >= t] = 1
        
        # Connected components.
        lbl, numcc = label(im)
        # Size threshold.
        min_size = 200 # pixels
        box = []
        print("Number of connected components is: " + str(numcc))
        for i in range(1, numcc + 1):
            py, px = np.nonzero(lbl == i)
            if len(py) < min_size:
                im[lbl == i] = 0
                continue
            
            xmin, xmax, ymin, ymax = px.min(), px.max(), py.min(), py.max()
            # Four corners and centroid.
            if (ymax-ymin) * (xmax-xmin) < 200000:
                continue
            box.append([
                        [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)],
                        (np.mean(px), np.mean(py))])
        return im.astype(np.uint8) * 255, box
    orig = pil_im
    im, box = boxes(orig)
    elements = []
    for c in cnts:
        rect = cv2.minAreaRect(c)
        min_box = cv2.cv.BoxPoints(rect) if imutils.is_cv2() else cv2.boxPoints(rect)
        min_box = np.int0(min_box)
        min_x = min(p[0] for p in min_box)
        max_x = max(p[0] for p in min_box)
        min_y = min(p[1] for p in min_box)
        max_y = max(p[1] for p in min_box)
        flag = True
        if cv2.contourArea(c)>100:
            for b, centroid in box:
                if min_x <= b[1][0] and max_x <= b[1][0] and min_x >= b[0][0] and max_x>=b[0][0] and min_y <= b[2][1] and max_y<= b[2][1] and min_y>= b[0][1] and max_y>=b[0][1]:
                    flag=False
            if flag:
                if (max_x-min_x)>450 and (max_y-min_y)<= 100:
                    cv2.drawContours(warped, [min_box], -1, (0,255,0),3)
                    elements.append(Line([min_x, max_x, min_y, max_y]))
        else:
            continue
    for b, centroid in box:
        cv2.rectangle(warped, (b[0][0], b[0][1]), (b[1][0], b[2][1]), (0,255,0))
        elements.append(Box([b[0][0], b[1][0], b[0][1], b[3][1]]))
    elements.sort(key=lambda element: element.coordinates[2])
    toReturn = []
    i=0
    while i<len(elements):
        if not elements[i].box:
            img = warped[elements[i].coordinates[3] - 300 :elements[i].coordinates[3], 0:elements[i].coordinates[1]]
            pillow = Image.fromarray(img)
            text = pytesseract.image_to_string(pillow)
            for char in text:
                if not char.isalnum():
                    text = text.replace(char,"")
                print(text)
                toReturn.append(["HEAD",text])
                i+=1
        else:
            j=i
            while elements[j].box and j!=len(elements)-1:
                j+=1
            if not elements[j].box:
                if i+2==j:
                    min_y = max(elements[i].coordinates[3], elements[i+1].coordinates[3])
                    img = warped[min_y:elements[j].coordinates[2]-300 , 0:warped.shape[:2][1]]
                    cv2.imwrite("passed_in1.png", img)
                    pillow = Image.fromarray(img)
                    text = pytesseract.image_to_string(pillow)
                    img1 = warped[elements[i].coordinates[2]: elements[i].coordinates[3],elements[i].coordinates[0]:elements[i].coordinates[1]]
                    x = randint(1, 1000000)
                    cv2.imwrite(str(x)+ ".jpg", img1)
                    upload_file(str(x)+ ".jpg") #generate large number
                    url1 = get_base_url()+get_id_from_title(str(x)+ ".jpg")
                    img2 = warped[elements[i+1].coordinates[2]: elements[i+1].coordinates[3], elements[i+1].coordinates[0]:elements[i+1].coordinates[1]]
                    x = randint(1, 1000000)
                    cv2.imwrite(str(x)+ ".jpg", img2)
                    upload_file(str(x)+ ".jpg") #generate large number
                    url2 = get_base_url()+get_id_from_title(str(x)+ ".jpg")
                    toReturn.append(["IMAGE", [url1, url2]])
                    toReturn.append(["TEXT", text])
                    print(text)
                    i+=2
                elif i+1==j:
                    img = warped[elements[i].coordinates[3]:elements[j].coordinates[2]-300 , 0:warped.shape[:2][1]]
                    pillow = Image.fromarray(img)
                    text = pytesseract.image_to_string(pillow)
                    img1 = warped[elements[i].coordinates[2]: elements[i].coordinates[3],elements[i].coordinates[0]:elements[i].coordinates[1]]
                    x = randint(1, 1000000)
                    cv2.imwrite(str(x)+ ".jpg", img1)
                    upload_file(str(x)+ ".jpg") #generate large number
                    url = get_base_url()+get_id_from_title(str(x)+ ".jpg")
                    toReturn.append(["IMAGE", [url]])
                    toReturn.append(["TEXT", text])
                    print(text)
                    i+=1
            else:
                if i<j:
                    min_y = max(elements[i].coordinates[3], elements[i+1].coordinates[3])
                    img = warped[min_y:warped.shape[:2][0], 0:warped.shape[:2][1]]
                    cv2.imwrite("passed_in.png", img)
                    pillow = Image.fromarray(img)
                    text = pytesseract.image_to_string(pillow)
                    img1 = warped[elements[i].coordinates[2]: elements[i].coordinates[3], elements[i].coordinates[0]:elements[i].coordinates[1]]
                    x = randint(1, 1000000)
                    cv2.imwrite(str(x)+ ".jpg", img1)
                    upload_file(str(x)+ ".jpg") #generate large number
                    url1 = get_base_url()+get_id_from_title(str(x)+ ".jpg")
                    img2 = warped[elements[i+1].coordinates[2]: elements[i+1].coordinates[3], elements[i+1].coordinates[0]:elements[i+1].coordinates[1]]
                    x = randint(1, 1000000)
                    cv2.imwrite(str(x)+ ".jpg", img2)
                    upload_file(str(x)+ ".jpg") #generate large number
                    url2 = get_base_url()+get_id_from_title(str(x)+ ".jpg")
                    toReturn.append(["IMAGE", [url1, url2]])
                    toReturn.append(["TEXT", text])
                    print(text)
                    i+=2
                else:
                    img = warped[elements[i].coordinates[3]:warped.shape[:2][0], 0:warped.shape[:2][1]]
                    cv2.imwrite("passed_in.png", img)
                    pillow = Image.fromarray(img)
                    text = pytesseract.image_to_string(pillow)
                    img1 = warped[elements[i].coordinates[2]: elements[i].coordinates[3],elements[i].coordinates[0]:elements[i].coordinates[1]]
                    x = randint(1, 1000000)
                    cv2.imwrite(str(x)+ ".jpg", img1)
                    upload_file(str(x)+ ".jpg") #generate large number
                    url = get_base_url()+get_id_from_title(str(x)+ ".jpg")
                    toReturn.append(["IMAGE", [url]])
                    toReturn.append(["TEXT", text])
                    print(text)
                    i+=1

    return toReturn
