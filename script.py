import cv2
import requests
import threading
import numpy as np

# Zmienna globalna do przechowywania informacji o naciśnięciu klawisza Escape
escape_pressed = False

# Funkcja obsługująca zdarzenia z klawiatury
def on_keyboard_event(event):
    global escape_pressed
    if event == 27:  # 27 to kod klawisza Escape
        escape_pressed = True

def stream_video_to_server(server_url, camera_id, camera_name):
    video = cv2.VideoCapture(camera_id)
    
    while not escape_pressed:
        ret, frame = video.read()
        if not ret:
            break

        _, img_encoded = cv2.imencode('.jpg', frame)
        img_bytes = img_encoded.tobytes()

        try:
            # Wysyłanie obrazu do serwera
            response = requests.post(f"{server_url}/upload/{camera_id}", data=img_bytes, headers={"Camera-Name": camera_name})
            print(response.text)
        except Exception as e:
            print("Error:", e)

    video.release()

if __name__ == "__main__":
    server_url = "http://127.0.0.1:5000"  # Adres serwera

    # Ustawienie funkcji obsługującej zdarzenia z klawiatury
    cv2.namedWindow("Keyboard Listener")
    cv2.setMouseCallback("Keyboard Listener", on_keyboard_event)

    # Dla każdej kamery uruchom osobny wątek
    threads = []
    cameras = [{"camera_id": 0, "camera_name": "camera1"},
               {"camera_id": 1, "camera_name": "camera2"},
               {"camera_id": 2, "camera_name": "camera3"}]  # Lista konfiguracji kamer

    for cam in cameras:
        thread = threading.Thread(target=stream_video_to_server, args=(server_url, cam["camera_id"], cam["camera_name"]))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Zamknięcie okien po zakończeniu pracy wątków
    cv2.destroyAllWindows()
