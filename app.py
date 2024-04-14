from flask import Flask, render_template, send_from_directory, redirect, session
from select_file import VideoManager

app = Flask(__name__)

VIDEO_DIRECTORY = '/Users/georg/Videos/Captures/'
video_manager = VideoManager(VIDEO_DIRECTORY)

@app.route('/')
def main():
    vid = session.get("video")
    if vid is None:
        vid = video_manager.get_latest_video()
    return render_template('index.html', path_to_video=f"/video/{vid}")

@app.route('/video/<filename>')
def video(filename):
    # Serve the video file using send_from_directory
    return send_from_directory(VIDEO_DIRECTORY, filename)

@app.route('/next_video')
def next_video():
    session['video'] = video_manager.get_random_video(VIDEO_DIRECTORY, 1)
    return redirect('/')
