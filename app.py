from flask import Flask, render_template, send_from_directory, redirect
from select_file import get_random_video

app = Flask(__name__)

VIDEO_DIRECTORY = '/Users/georg/Videos/Captures/'
app.config['random_video'] = get_random_video(VIDEO_DIRECTORY)

@app.route('/')
def main():
    vid = app.config['random_video']
    return render_template('index.html', path_to_video=f"/video/{vid}")

@app.route('/video/<filename>')
def video(filename):
    # Serve the video file using send_from_directory
    return send_from_directory(VIDEO_DIRECTORY, filename)

@app.route('/next_video')
def next_video():
    next_vid = get_random_video(VIDEO_DIRECTORY, 1)
    app.config['random_video'] = next_vid
    return redirect('/')
