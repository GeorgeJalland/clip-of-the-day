from flask import Flask, render_template, send_from_directory, redirect, session
from urllib.parse import quote
from select_file import VideoManager

app = Flask(__name__)
app.secret_key = 'dc726efe259959c9c259996fa4ef418e'

VIDEO_DIRECTORY = '/Users/georg/OneDrive/Captures/'
video_manager = VideoManager(VIDEO_DIRECTORY)

@app.route('/')
def main():
    print(session.get('video'))
    vid = session.get('video', video_manager.get_latest_video())
    return render_template('index.html', path_to_video=f"/video/{quote(vid)}")

@app.route('/video/<filename>')
def video(filename):
    # Serve the video file using send_from_directory
    return send_from_directory(VIDEO_DIRECTORY, filename)

@app.route('/next-video')
def next_video():
    session['video'] = video_manager.get_random_video(1)
    return redirect('/')

@app.route('/original')
def original():
    session.pop('video', None)
    return redirect('/')

