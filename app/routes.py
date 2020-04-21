import io
from app import app
from flask import Flask, request, jsonify
from pydub import AudioSegment
from dejavu import Dejavu
from dejavu.recognize import FileRecognizer
from app.config import config

import os

# Markdown formatter
import markdown

# Delete warning message
import warnings
warnings.filterwarnings("ignore", category=Warning)

PATH_FOLDER = "temp"
FILE_NAME = "tmp.mp3"
FILE_PATH = PATH_FOLDER + "/" + FILE_NAME

# CREATE folder if unexisting
if not os.path.isdir(FILE_PATH.split("/")[0]):
    os.mkdir(PATH_FOLDER)

# CREATE file if unexisting
if not os.path.isfile(FILE_PATH):
    open(FILE_PATH, 'w+').close()


@app.route('/')
@app.route('/index')
def index():
    # Read md file
    with open("readme.md", "r") as readme_file:
        md_template_string = markdown.markdown(readme_file.read(),extensions=["fenced_code"])

    # Add styles
    md_css_string = '<style>@media print{*,:after,:before{background:0 0!important;color:#000!important;box-shadow:none!important;text-shadow:none!important}a,a:visited{text-decoration:underline}a[href]:after{content:" (" attr(href) ")"}abbr[title]:after{content:" (" attr(title) ")"}a[href^="#"]:after,a[href^="javascript:"]:after{content:""}blockquote,pre{border:1px solid #999;page-break-inside:avoid}thead{display:table-header-group}img,tr{page-break-inside:avoid}img{max-width:100%!important}h2,h3,p{orphans:3;widows:3}h2,h3{page-break-after:avoid}}@media screen and (min-width:32rem) and (max-width:48rem){html{font-size:15px}}html{font-size:16px}body{line-height:1.85}.splendor-p,p{font-size:1rem;margin-bottom:1.3rem}.splendor-h1,.splendor-h2,.splendor-h3,.splendor-h4,h1,h2,h3,h4{margin:1.414rem 0 .5rem;font-weight:inherit;line-height:1.42}.splendor-h1,h1{margin-top:0;font-size:3.998rem}.splendor-h2,h2{font-size:2.827rem}.splendor-h3,h3{font-size:1.999rem}.splendor-h4,h4{font-size:1.414rem}.splendor-h5,h5{font-size:1.121rem}.splendor-h6,h6{font-size:.88rem}.splendor-small,small{font-size:.707em}canvas,iframe,img,select,svg,textarea,video{max-width:100%}@import url(http://fonts.googleapis.com/css?family=Merriweather:300italic,300);html{font-size:18px;max-width:100%}body{color:#444;font-family:Merriweather,Georgia,serif;margin:0;max-width:100%}:not(div):not(img):not(body):not(html):not(li):not(blockquote):not(p),p{margin:1rem auto;max-width:36rem;padding:.25rem}div,div img{width:100%}blockquote p{font-size:1.5rem;font-style:italic;margin:1rem auto;max-width:48rem}li{margin-left:2rem}h1{padding:4rem 0!important}p{color:#555;height:auto;line-height:1.45}code,pre{font-family:Menlo,Monaco,"Courier New",monospace}pre{background-color:#fafafa;font-size:.8rem;overflow-x:scroll;padding:1.125em}a,a:visited{color:#3498db}a:active,a:focus,a:hover{color:#2980b9}</style>'
    md_template = md_css_string + md_template_string

    return md_template

@app.route('/check_connexion')
def connexion_test():
    return jsonify({'status': "OK"})
    

@app.route('/find_sound', methods=['POST', 'GET'])
def recognize_song():
    print("=" * 50)
    print("List uploaded files: {}".format(request.files.getlist('uploaded_file')))
    files = request.files.getlist('uploaded_file')

    artist = ""
    title = ""

    if files and len(files) > 0:
        print("\t Reading song uploaded ...")        
        # Read song from parameters -> download it as mp3 file    
        b = io.BytesIO(files[0].read())
        song = AudioSegment.from_file(b, format="3gp")

        song.export(FILE_PATH, format="mp3")

        print("\t File song read\n\t Song recognition started...")        
        # create a Dejavu instance
        djv = Dejavu(config)

        # Recognize audio from a file
        song_found = djv.recognize(FileRecognizer, FILE_PATH)

        print("\t Song recognition finished")

        if song_found: 
            song_name = song_found.get('song_name').split("--")
            artist = song_name[0]
            title = song_name[1]
            print("\t Song:\n\t\t - Music: {}\n\t\t - Artist: {}".format(title, artist))        


    print("\t Return response")        
    print("=" * 50)
    return jsonify({
        'artist': artist,
        'title': title
        })