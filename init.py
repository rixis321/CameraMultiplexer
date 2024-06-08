import tkinter as tk
from tkinter import messagebox, filedialog
import cv2
import os
import subprocess

class App:
    def __init__(self, master):
        self.master = master
        master.title("Camera Multiplexer CCTV")
        master.geometry("500x200")

        self.label = tk.Label(master, text="Kliknij przycisk, aby włączyć lub wyłączyć program:")
        self.label.pack()

        self.button_toggle = tk.Button(master, text="Włącz program", command=self.toggle_program)
        self.button_toggle.pack()
        self.button_toggle.config(width=20, height=2)

        self.button_compress = tk.Button(master, text="Wybierz plik i skompresuj", command=self.compress_file)
        self.button_compress.pack()
        self.button_compress.config(width=20, height=2)

        self.button_decompress = tk.Button(master, text="Wybierz skompresowany plik i zdekompresuj", command=self.decompress_file)
        self.button_decompress.pack()
        self.button_decompress.config(width=35, height=2)

        self.program_running = False
        self.script_process = None
        self.server_processes = []

    def toggle_program(self):
        if not self.program_running:
            self.start_program()
        else:
            self.stop_program()

    def start_program(self):
        try:
            
            server_proc1 = subprocess.Popen(["python", "./server.py"])
            self.server_processes.append(server_proc1)
           
            server_proc2 = subprocess.Popen(["python", "./storage_server.py"])
            self.server_processes.append(server_proc2)
            
            self.script_process = subprocess.Popen(["python", "./script.py"])
            self.program_running = True
            self.button_toggle.config(text="Wyłącz program")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można uruchomić programu: {str(e)}")

    def stop_program(self):
        try:
           
            for server_proc in self.server_processes:
                server_proc.terminate()

            
            if self.script_process:
                self.script_process.terminate()
                self.script_process.wait()

            self.program_running = False
            self.button_toggle.config(text="Włącz program")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można zamknąć programu: {str(e)}")

    def compress_file(self):
        try:
            
            file_path = filedialog.askopenfilename(title="Wybierz plik wideo", filetypes=[("Pliki AVI", "*.avi")])
            if file_path:
                
                if os.path.exists(file_path):
                    
                    compressed_file_path = self.compress_with_xvid(file_path)
                    messagebox.showinfo("Sukces", f"Plik został skompresowany jako {compressed_file_path}")
                else:
                    messagebox.showerror("Błąd", "Wybrany plik nie istnieje")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas kompresji pliku: {str(e)}")

    def compress_with_xvid(self, input_file):
        try:
           
            base_name, _ = os.path.splitext(input_file)
            compressed_file_path = f"{base_name}_compressed.avi"

           
            video_capture = cv2.VideoCapture(input_file)
            frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(video_capture.get(cv2.CAP_PROP_FPS))

          
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(compressed_file_path, fourcc, fps, (frame_width, frame_height))

           
            while True:
                ret, frame = video_capture.read()
                if not ret:
                    break
                out.write(frame)

           
            video_capture.release()
            out.release()

            return compressed_file_path
        except Exception as e:
            error_message = f"Wystąpił błąd podczas kompresji pliku: {str(e)}"
            messagebox.showerror("Błąd", error_message)

    def decompress_file(self):
        try:
          
            file_path = filedialog.askopenfilename(title="Wybierz skompresowany plik wideo", filetypes=[("Pliki AVI", "*.avi")])
            if file_path:
               
                if os.path.exists(file_path):
                   
                    decompressed_file_path = self.decompress_with_xvid(file_path)
                    messagebox.showinfo("Sukces", f"Plik został zdekompresowany jako {decompressed_file_path}")
                else:
                    messagebox.showerror("Błąd", "Wybrany plik nie istnieje")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas dekompresji pliku: {str(e)}")

    def decompress_with_xvid(self, input_file):
        try:
          
            base_name, _ = os.path.splitext(input_file)
            decompressed_file_path = f"{base_name}_decompressed.avi"

            video_capture = cv2.VideoCapture(input_file)
            frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(video_capture.get(cv2.CAP_PROP_FPS))

            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(decompressed_file_path, fourcc, fps, (frame_width, frame_height))

        
            while True:
                ret, frame = video_capture.read()
                if not ret:
                    break
                out.write(frame)

            video_capture.release()
            out.release()

            return decompressed_file_path
        except Exception as e:
            error_message = f"Wystąpił błąd podczas dekompresji pliku: {str(e)}"
            messagebox.showerror("Błąd", error_message)

root = tk.Tk()
app = App(root)
root.mainloop()
