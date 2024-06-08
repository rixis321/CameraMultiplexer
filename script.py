import cv2
import requests
import threading

def stream_video_to_server(server_url, camera_id, camera_name):
    video = cv2.VideoCapture(camera_id)
    
    while True:
        ret, frame = video.read()
        if not ret:
            break

        _, img_encoded = cv2.imencode('.jpg', frame)
        img_bytes = img_encoded.tobytes()

        try:
          
            response = requests.post(f"{server_url}/upload/{camera_id}", data=img_bytes, headers={"Camera-Name": camera_name})
            print(response.text)
        except Exception as e:
            print("Error:", e)

    video.release()

if __name__ == "__main__":
    server_url = "http://127.0.0.1:5000" 

    threads = []
    cameras = [{"camera_id": 0, "camera_name": "camera1"},
               {"camera_id": 1, "camera_name": "camera2"},
               {"camera_id": 2, "camera_name": "camera3"}] 

    for cam in cameras:
        thread = threading.Thread(target=stream_video_to_server, args=(server_url, cam["camera_id"], cam["camera_name"]))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
