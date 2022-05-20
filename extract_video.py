from pathlib import Path
import cv2 as cv
import tkinter as tk
from tkinter import W, ttk, filedialog, messagebox

def extract():
    if source_path.get() == "" or (is_same_directory.get() != "True" and destination_path.get() == ""):
        return

    #Open the file
    cap = cv.VideoCapture(source_path.get())
    if not cap.isOpened():
        return
    
    #Retrieve the filename
    filename = Path(source_path.get()).stem
    
    #Set the destination directory based on the checkbox
    if is_same_directory.get() == "True":
        destination_directory = str(Path(source_path.get()).parent) + "/images"
        #Make the directory if it doesn't exist
        Path(destination_directory).mkdir(parents=False, exist_ok=True)
    else:
        destination_directory = destination_path.get()
    
    #Start to extract
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # print(cap.get(cv.CAP_PROP_POS_FRAMES), cap.get(cv.CAP_PROP_FRAME_COUNT), cap.get(cv.CAP_PROP_FPS))
        if not cv.imwrite(destination_directory + "/" + filename + "_frame" + str(cap.get(cv.CAP_PROP_POS_FRAMES)).split('.')[0] + ".jpg", frame):
            break
    
    messagebox.showinfo("Terminé!", "L'extraction est terminée")
    cap.release()

def destination_checkbox_clicked():
    if is_same_directory.get() == "True":
        file_destination_input.config(state="disabled")
        file_destination_browse_button.config(state="disabled")
    else:
        file_destination_input.config(state="normal")
        file_destination_browse_button.config(state="normal")

root = tk.Tk()
root.title('Extraction d\'images de vidéo')
default_options = {'padx': 5, 'pady': 5}
frame = ttk.Frame(root)

file_source_label = ttk.Label(frame, text="Fichier source").grid(row=0, columnspan=3, **default_options, sticky=W)
source_path = tk.StringVar()
file_source_input = ttk.Entry(frame, textvariable=source_path, width=50).grid(row=1, column=0, **default_options)
file_source_browse_button = ttk.Button(frame, text="Parcourir", command=lambda: source_path.set(filedialog.askopenfilename())).grid(row=1, column=1, **default_options)

is_same_directory = tk.StringVar()
is_same_directory.set("True")
destination_checkbox = ttk.Checkbutton(frame, text="Extraire dans le même dossier (/images)", command=destination_checkbox_clicked, variable=is_same_directory, onvalue="True", offvalue="False")
destination_checkbox.grid(row=2, columnspan=3, **default_options, sticky=W)

file_destination_label = ttk.Label(frame, text="Dossier de destination").grid(row=3, columnspan=3, **default_options, sticky=W)
destination_path = tk.StringVar()
file_destination_input = ttk.Entry(frame, textvariable=destination_path, width=50, state="disabled")
file_destination_input.grid(row=4, column=0, **default_options)
file_destination_browse_button = ttk.Button(frame, text="Parcourir", command=lambda: destination_path.set(filedialog.askdirectory()), state="disabled")
file_destination_browse_button.grid(row=4, column=1, **default_options)

start_extraction_button = ttk.Button(frame, text="Extraire", command=extract).grid(row=5, columnspan=3, **default_options)

frame.grid(padx=10, pady=10)
root.mainloop()