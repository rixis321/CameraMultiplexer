from flask import Flask, request, jsonify, send_from_directory
import cv2
import numpy as np
import threading
import os
from datetime import datetime

app = Flask(__name__)

video_writer = None
frame_size = None
output_dir = "recorded_videos"
os.makedirs(output_dir, exist_ok=True)

lock = threading.Lock() 


def save_video_frame(frame):
    global video_writer, frame_size, lock
    try:
        if video_writer is None:
            height, width = frame.shape[:2]
            frame_size = (width, height)
            fourcc = cv2.VideoWriter_fourcc(*'XVID')

            now = datetime.now()
            current_time = now.strftime("%Y-%m-%d_%H-%M-%S")
            video_writer = cv2.VideoWriter(os.path.join(output_dir, f"{current_time}.avi"), fourcc, 30.0, frame_size)

        with lock:
            video_writer.write(frame)
            print("Frame written to video file")
    except Exception as e:
        print(f"Error while writing frame to video: {e}")

@app.route('/upload/0', methods=['POST'])
def upload():
    try:
        img_bytes = request.data
        frame = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
        print("Received frame for recording")
        threading.Thread(target=save_video_frame, args=(frame,)).start()
        return "Image received and saved successfully."
    except Exception as e:
        print(f"Error while receiving frame: {e}")
        return f"Error: {str(e)}"
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, threaded=True, debug=False)
