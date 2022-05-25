from pathlib import Path
import cv2 as cv
import tkinter as tk
from tkinter import W, ttk, filedialog, messagebox

cap = 0
step = 0
in_progress = False
destination_directory = ""
filename = ""
start_frame = 0
end_frame = 0

def nextStep():
    global step

    if not openFile():
        return
        
    step += 1
    window_step1.grid_forget()
    window_step2.grid(padx=10, pady=10)
    info_file_name_variable.set(Path(source_path.get()).name)
    info_fps_variable.set(str(cap.get(cv.CAP_PROP_FPS)) + "fps")
    info_duree_variable.set(str(cap.get(cv.CAP_PROP_FRAME_COUNT) / cap.get(cv.CAP_PROP_FPS)) + "s")

def previousStep():
    global cap
    cap.release()

    step =- 1
    window_step2.grid_forget()
    window_step1.grid(padx=10, pady=10)

def openFile():
    global cap

    if source_path.get() == "" or (is_same_directory.get() != "True" and destination_path.get() == ""):
        messagebox.showerror('Erreur', 'Fichier source ou destination invalide')
        return False

    #Open the file
    cap = cv.VideoCapture(source_path.get())
    if not cap.isOpened():
        messagebox.showerror('Erreur', 'Impossible d\'ouvrir le fichier')
        return False
    
    return True

def runExtraction():
    global in_progress, destination_directory, filename, start_frame, end_frame, cap
    in_progress = True

    #Retrieve the filename
    filename = Path(source_path.get()).stem
    
    #Set the destination directory based on the checkbox
    if is_same_directory.get() == "True":
        destination_directory = str(Path(source_path.get()).parent) + "/images"
        #Make the directory if it doesn't exist
        Path(destination_directory).mkdir(parents=False, exist_ok=True)
    else:
        destination_directory = destination_path.get()
    
    is_time_valid, debut, fin = validateTimes(start_time.get(), end_time.get(), cap.get(cv.CAP_PROP_FRAME_COUNT) / cap.get(cv.CAP_PROP_FPS))
    if not is_time_valid:
        messagebox.showerror("Temps invalide", "Les temps entrés ne sont pas valides")
        return

    # Set the start frame
    cap.set(cv.CAP_PROP_POS_FRAMES, debut * cap.get(cv.CAP_PROP_FPS))
    start_frame = cap.get(cv.CAP_PROP_POS_FRAMES)
    end_frame = fin * cap.get(cv.CAP_PROP_FPS)
    extract()

def extract():
    global in_progress, destination_directory, filename, start_frame, end_frame
    done = False
    
    if not in_progress:
        return
    
    ret, frame = cap.read()
    if not ret or cap.get(cv.CAP_PROP_POS_FRAMES) >= end_frame:
        in_progress = False
        done = True

    if in_progress and not cv.imwrite(destination_directory + "/" + filename + "_frame" + str(cap.get(cv.CAP_PROP_POS_FRAMES)).split('.')[0] + ".jpg", frame):
        in_progress = False

    progress_label.set(str(round(cap.get(cv.CAP_PROP_POS_FRAMES) - start_frame)) + "/" + str(round(end_frame - start_frame)))
    progressbar['value'] = round((cap.get(cv.CAP_PROP_POS_FRAMES) - start_frame) / (end_frame - start_frame) * 100)

    if done:
        messagebox.showinfo("Terminé!", "L'extraction est terminée")
        cap.release()
        in_progress = False

    root.after(2, extract)

def validateTimes(debut, fin, max):
    try:
        debut = int(debut)
        fin = int(fin)
    except:
        return (False, debut, fin)

    if (debut < 0 or fin < 1 or fin > max or debut == fin or fin < debut):
        return (False, debut, fin)
    return (True, debut, fin)

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
window_step1 = ttk.Frame(root)
window_step2 = ttk.Frame(root)

# Window 1 components
file_source_label = ttk.Label(window_step1, text="Fichier source").grid(row=0, columnspan=3, **default_options, sticky=W)
source_path = tk.StringVar()
file_source_input = ttk.Entry(window_step1, textvariable=source_path, width=50).grid(row=1, column=0, **default_options)
file_source_browse_button = ttk.Button(window_step1, text="Parcourir", command=lambda: source_path.set(filedialog.askopenfilename())).grid(row=1, column=1, **default_options)

is_same_directory = tk.StringVar()
is_same_directory.set("True")
destination_checkbox = ttk.Checkbutton(window_step1, text="Extraire dans le même dossier (/images)", command=destination_checkbox_clicked, variable=is_same_directory, onvalue="True", offvalue="False")
destination_checkbox.grid(row=2, columnspan=3, **default_options, sticky=W)

file_destination_label = ttk.Label(window_step1, text="Dossier de destination").grid(row=3, columnspan=3, **default_options, sticky=W)
destination_path = tk.StringVar()
file_destination_input = ttk.Entry(window_step1, textvariable=destination_path, width=50, state="disabled")
file_destination_input.grid(row=4, column=0, **default_options)
file_destination_browse_button = ttk.Button(window_step1, text="Parcourir", command=lambda: destination_path.set(filedialog.askdirectory()), state="disabled")
file_destination_browse_button.grid(row=4, column=1, **default_options)

next_step_button = ttk.Button(window_step1, text="Suivant", command=nextStep).grid(row=5, columnspan=3, **default_options)

# Window 2 components
ttk.Label(window_step2, text="Nom du fichier:").grid(row=0, column=0, sticky=W)
info_file_name_variable = tk.StringVar()
ttk.Label(window_step2, textvariable=info_file_name_variable).grid(row=0, column=1, sticky=W)

ttk.Label(window_step2, text="FPS:").grid(row=1, column=0, sticky=W)
info_fps_variable = tk.StringVar()
ttk.Label(window_step2, textvariable=info_fps_variable).grid(row=1, column=1, sticky=W)

ttk.Label(window_step2, text="Durée:").grid(row=2, column=0, sticky=W)
info_duree_variable = tk.StringVar()
ttk.Label(window_step2, textvariable=info_duree_variable).grid(row=2, column=1, sticky=W)

ttk.Label(window_step2, text="Temps de début (s):").grid(row=3, column=0, sticky=W)
start_time = tk.StringVar()
ttk.Entry(window_step2, textvariable=start_time, width=4).grid(row=3, column=1, sticky=W)

ttk.Label(window_step2, text="Temps de fin (s):").grid(row=4, column=0, sticky=W)
end_time = tk.StringVar()
ttk.Entry(window_step2, textvariable=end_time, width=4).grid(row=4, column=1, sticky=W)

progressbar = ttk.Progressbar(window_step2, length=250, mode="determinate")
progressbar.grid(row=5, columnspan=3, **default_options)
progress_label = tk.StringVar()
ttk.Label(window_step2, textvariable=progress_label).grid(row=6, columnspan=3)

previous_step_button = ttk.Button(window_step2, text="Précédent", command=previousStep).grid(row=7, column=0, **default_options)
start_extraction_button = ttk.Button(window_step2, text="Extraire", command=runExtraction).grid(row=7, column=1, **default_options)


window_step1.grid(padx=10, pady=10)
root.mainloop()