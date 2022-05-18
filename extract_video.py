from pathlib import Path
import cv2 as cv
import tkinter as tk
from tkinter import W, ttk, filedialog

def extract():
    if source_path.get() == "" or destination_path.get() == "":
        return

    cap = cv.VideoCapture(source_path.get())
    if not cap.isOpened():
        return
    
    filename = Path(source_path.get()).stem
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        print(cap.get(cv.CAP_PROP_POS_FRAMES), cap.get(cv.CAP_PROP_FRAME_COUNT), cap.get(cv.CAP_PROP_FPS))
        if not cv.imwrite(destination_path.get() + "/" + filename + "_frame" + str(cap.get(cv.CAP_PROP_POS_FRAMES)).split('.')[0] + ".jpg", frame):
            break
         
    cap.release()

root = tk.Tk()
root.title('Extraction d\'images de vidéo')
default_options = {'padx': 5, 'pady': 5}
frame = ttk.Frame(root)

file_source_label = ttk.Label(frame, text="Fichier source").grid(row=0, columnspan=3, **default_options, sticky=W)
source_path = tk.StringVar()
file_source_input = ttk.Entry(frame, textvariable=source_path, width=50).grid(row=1, column=0, **default_options)
file_source_browse_button = ttk.Button(frame, text="Parcourir", command=lambda: source_path.set(filedialog.askopenfilename())).grid(row=1, column=1, **default_options)

file_destination_label = ttk.Label(frame, text="Dossier de destination").grid(row=2, columnspan=3, **default_options, sticky=W)
destination_path = tk.StringVar()
file_destination_input = ttk.Entry(frame, textvariable=destination_path, width=50).grid(row=3, column=0, **default_options)
file_destination_browse_button = ttk.Button(frame, text="Parcourir", command=lambda: destination_path.set(filedialog.askdirectory())).grid(row=3, column=1, **default_options)

start_extraction_button = ttk.Button(frame, text="Extraire", command=extract).grid(row=4, columnspan=3, **default_options)

frame.grid(padx=10, pady=10)
root.mainloop()