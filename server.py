import cv2
import requests
import threading
import numpy as np
from flask import Flask, jsonify, Response, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

video_capture_dict = {}
frame_buffers = {}
recording_server_url = "http://127.0.0.1:5001" 

def generate():
    global frame_buffers
    while True:
        combined_frame = None
        for camera_id, frame_buffer in frame_buffers.items():
            frame = frame_buffer
            if frame is not None:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame = cv2.resize(frame, (frame.shape[1] // 2, frame.shape[0] // 2))
                if combined_frame is None:
                    combined_frame = frame
                else:
                    frame = cv2.resize(frame, (combined_frame.shape[1], combined_frame.shape[0]))
                    combined_frame = cv2.hconcat([combined_frame, frame])
        
        if combined_frame is not None:
            _, img_encoded = cv2.imencode('.jpg', combined_frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
            frame_bytes = img_encoded.tobytes()
            

            try:
                response = requests.post(f"{recording_server_url}/upload/0", data=frame_bytes)
            except Exception as e:
                print(f"Failed to send frame to recording server: {e}")

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed_vlc')
def video_feed_vlc():
    return Response(generate(),
                    mimetype='application/octet-stream')

@app.route('/video_feed/all')
def video_feed_all():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed/<int:camera_id>')
def video_feed(camera_id):
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera_list')
def camera_list():
    return jsonify({"cameras": cameras})

@app.route('/upload/<int:camera_id>', methods=['POST'])
def upload(camera_id):
    global frame_buffers
    try:
        img_bytes = request.data
        frame = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
        frame_buffers[camera_id] = frame
        return "Image received successfully."
    except Exception as e:
        return f"Error: {str(e)}"

def start_server(cameras):
    global video_capture_dict
    for cam in cameras:
        video_capture_dict[cam["camera_id"]] = cv2.VideoCapture(cam["camera_id"])
        frame_buffers[cam["camera_id"]] = None
    app.run(host='0.0.0.0', threaded=True, debug=False)
    
if __name__ == "__main__":
    cameras = [{"camera_id": 0, "camera_name": "camera1"},
               {"camera_id": 1, "camera_name": "camera2"},
               {"camera_id": 2, "camera_name": "camera3"}]
    start_server(cameras)
