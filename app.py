from flask import Flask, render_template, send_from_directory, redirect, session
from select_file import VideoManager

app = Flask(__name__)
app.secret_key = 'dc726efe259959c9c259996fa4ef418e'

VIDEO_DIRECTORY = '/Users/georg/Videos/Captures/'
video_manager = VideoManager(VIDEO_DIRECTORY)

@app.route('/')
def main():
    vid = session.get('video')
    if vid is None:
        vid = session['video'] = video_manager.get_latest_video()
    print(session['video'])
    return render_template('index.html', path_to_video=f"/video/{vid}")

@app.route('/video/<filename>')
def video(filename):
    # Serve the video file using send_from_directory
    return send_from_directory(VIDEO_DIRECTORY, filename)

@app.route('/next_video')
def next_video():
    session['video'] = video_manager.get_random_video(1)
    return redirect('/')
