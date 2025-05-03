import cv2
import os
import time

from common.logger import get_logger

class ThumbnailGenerator:
    def __init__(self):
        self.logger = get_logger(__name__)

    def generate(self, video_path: str, output_path: str, time_in_seconds: int = 0):
        self.logger.info(f"Generating thumbnail for {video_path}")

        cap = cv2.VideoCapture(video_path)

        cap.set(cv2.CAP_PROP_POS_MSEC, time_in_seconds * 1000)

        success, frame = cap.read()
        if success:
            cv2.imwrite(output_path, frame)
            self.logger.info(f"Thumbnail saved to {output_path}")
            cap.release()
            return output_path
        else:
            cap.release()
            self.logger.error(f"Failed to generate thumbnail for {video_path}")

    def delayed_generate(self, video_path: str, output_path:str, time_in_seconds: int = 3, delay_seconds: int = 1):
        """Generate thumbnail with a delay to ensure the video is fully written."""
        time.sleep(delay_seconds)
        return self.generate(video_path, output_path, time_in_seconds)

def get_thumbnail_path(video_path: str) -> str:
    video_name = os.path.basename(video_path)
    thumbnail_name = video_name.removesuffix(".mp4") + ".jpg"
    player_directory = os.path.dirname(video_path)
    return os.path.join(player_directory, "thumbnails", thumbnail_name)
