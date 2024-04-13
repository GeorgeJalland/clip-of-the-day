from flask import Flask, render_template, send_from_directory
from select_file import get_random_video

app = Flask(__name__)

video_directory = '/Users/georg/Videos/Captures/'
random_video = get_random_video(video_directory)

@app.route('/')
def main():
    return render_template('index.html', path_to_video=f"/video/{random_video}")

@app.route('/video/<filename>')
def video(filename):
    # Serve the video file using send_from_directory
    return send_from_directory(video_directory, filename)

@app.route('/next_video')
def next_video():
    return 