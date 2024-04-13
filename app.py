from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

random_video = 

@app.route('/')
def main():
    return render_template('index.html', path_to_video="/video/latest.mp4")

@app.route('/video/<filename>')
def video(filename):
    # Specify the directory containing the video file
    directory = '/Users/georg/Videos/Captures/'

    # Serve the video file using send_from_directory
    return send_from_directory(directory, filename)