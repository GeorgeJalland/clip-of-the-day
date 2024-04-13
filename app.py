from flask import Flask, render_template
from select_file import copy_file
import os

app = Flask(__name__)

@app.route('/')
def main():
    source_path="/Users/georg/Videos/Captures/latest.mp4"
    destination_path="/Users/georg/Desktop/Projects/rocket-serve/static/latest.mp4"
    if not os.path.isfile(destination_path):
        print("file copied")
        copy_file(source_path, destination_path)
    return render_template('index.html', path_to_video="/Users/georg/Videos/Captures/latest.mp4")