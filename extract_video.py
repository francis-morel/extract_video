from pathlib import Path
from typing import Tuple
import cv2 as cv
import tkinter as tk
from tkinter import W, ttk, filedialog, messagebox
import math
import threading


cap = 0
step = 0
in_progress = False
destination_directory = ""
filename = ""
start_frame = 0
end_frame = 0


def nextStep() -> None:
    global step

    if not openFile():
        return

    step += 1
    window_step1.grid_forget()
    window_step2.grid(padx=10, pady=10)
    info_file_name_variable.set(Path(source_path.get()).name)
    info_fps_variable.set(str(cap.get(cv.CAP_PROP_FPS)) + "fps")
    info_duree_variable.set(
        str(cap.get(cv.CAP_PROP_FRAME_COUNT) / cap.get(cv.CAP_PROP_FPS)) + "s"
    )


def previousStep() -> None:
    global cap
    cap.release()

    step = -1
    window_step2.grid_forget()
    window_step1.grid(padx=10, pady=10)


def openFile() -> bool:
    global cap

    if source_path.get() == "" or (
        is_same_directory.get() != "True" and destination_path.get() == ""
    ):
        messagebox.showerror("Erreur", "Fichier source ou destination invalide")
        return False

    # Open the file
    cap = cv.VideoCapture(source_path.get())
    if not cap.isOpened():
        messagebox.showerror("Erreur", "Impossible d'ouvrir le fichier")
        return False

    start_time.set("0")
    end_time.set(
        str(math.trunc(cap.get(cv.CAP_PROP_FRAME_COUNT) / cap.get(cv.CAP_PROP_FPS)) + 1)
    )

    return True


def runExtraction() -> None:

    global in_progress, destination_directory, filename, start_frame, end_frame, cap
    if not cap.isOpened():
        return
    in_progress = True

    # Retrieve the filename
    filename = Path(source_path.get()).stem

    # Set the destination directory based on the checkbox
    if is_same_directory.get() == "True":
        destination_directory = str(Path(source_path.get()).parent) + "/images"
        # Make the directory if it doesn't exist
        Path(destination_directory).mkdir(parents=False, exist_ok=True)
    else:
        destination_directory = destination_path.get()

    is_time_valid, debut, fin = validateTimes(
        int(start_time.get()), int(end_time.get())
    )
    if not is_time_valid:
        messagebox.showerror("Temps invalide", "Les temps entrés ne sont pas valides")
        return

    # Set the start frame
    cap.set(cv.CAP_PROP_POS_FRAMES, debut * cap.get(cv.CAP_PROP_FPS))
    start_frame = cap.get(cv.CAP_PROP_POS_FRAMES)
    end_frame = min(fin * cap.get(cv.CAP_PROP_FPS), cap.get(cv.CAP_PROP_FRAME_COUNT))
    thread = threading.Thread(target=extract)
    thread.daemon = True
    thread.start()


def stopExtraction() -> None:
    global in_progress
    in_progress = False
    setWidgetWhileExtracting(in_progress)
    progress_label.set("")
    progressbar["value"] = 0


def extract() -> None:
    global in_progress, destination_directory, filename, start_frame, end_frame, cap
    done = False

    if not in_progress or not cap.isOpened():
        return

    while in_progress:
        ret, frame = cap.read()
        if not ret or cap.get(cv.CAP_PROP_POS_FRAMES) >= end_frame:
            in_progress = False
            done = True

        min, sec, ms = msec_to_minute_seconde_msec(
            round(cap.get(cv.CAP_PROP_POS_FRAMES) / cap.get(cv.CAP_PROP_FPS) * 1000)
        )
        image_name = (
            destination_directory
            + "/"
            + filename
            + "_"
            + min
            + "m_"
            + sec
            + "s_"
            + ms
            + "ms"
            + ".jpg"
        )
        if not Path(image_name).is_file():
            if in_progress and not cv.imwrite(image_name, frame):
                in_progress = False

        progress_label.set(
            str(round(cap.get(cv.CAP_PROP_POS_FRAMES) - start_frame))
            + "/"
            + str(round(end_frame - start_frame))
        )
        progressbar["value"] = round(
            (cap.get(cv.CAP_PROP_POS_FRAMES) - start_frame)
            / (end_frame - start_frame)
            * 100
        )

        if done:
            cap.release()
            in_progress = False
            messagebox.showinfo("Extraction terminée!", "Extraction terminée!")

        setWidgetWhileExtracting(in_progress)


def msec_to_minute_seconde_msec(time: int) -> tuple[str, str, str]:
    timeleft = time
    min = math.floor(timeleft / 60000)
    timeleft -= min * 60000
    sec = math.floor(timeleft / 1000)
    timeleft -= sec * 1000
    return (str(min), "{:0>2}".format(sec), "{:0>4}".format(timeleft))


def setWidgetWhileExtracting(isExtracting: bool) -> None:
    if isExtracting:
        start_time_entry.config(state="disabled")
        end_time_entry.config(state="disabled")
        previous_step_button.config(state="disabled")
        start_extraction_button.config(state="disabled")
        stop_extraction_button.grid(row=7, column=1, **default_options)
    else:
        start_time_entry.config(state="normal")
        end_time_entry.config(state="normal")
        previous_step_button.config(state="normal")
        start_extraction_button.config(state="normal")
        stop_extraction_button.grid_forget()


def validateTimes(debut: int, fin: int) -> Tuple[bool, int, int]:
    if debut < 0 or fin < 1 or debut == fin or fin < debut:
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
root.title("Extraction d'images de vidéo")
default_options = {"padx": 5, "pady": 5}
window_step1 = ttk.Frame(root)
window_step2 = ttk.Frame(root)

# Window 1 components
file_source_label = ttk.Label(window_step1, text="Fichier source").grid(
    row=0, columnspan=3, **default_options, sticky=W
)
source_path = tk.StringVar()
file_source_input = ttk.Entry(window_step1, textvariable=source_path, width=50).grid(
    row=1, column=0, **default_options
)
file_source_browse_button = ttk.Button(
    window_step1,
    text="Parcourir",
    command=lambda: source_path.set(filedialog.askopenfilename()),
).grid(row=1, column=1, **default_options)

is_same_directory = tk.StringVar()
is_same_directory.set("True")
destination_checkbox = ttk.Checkbutton(
    window_step1,
    text="Extraire dans le même dossier (/images)",
    command=destination_checkbox_clicked,
    variable=is_same_directory,
    onvalue="True",
    offvalue="False",
)
destination_checkbox.grid(row=2, columnspan=3, **default_options, sticky=W)

file_destination_label = ttk.Label(window_step1, text="Dossier de destination").grid(
    row=3, columnspan=3, **default_options, sticky=W
)
destination_path = tk.StringVar()
file_destination_input = ttk.Entry(
    window_step1, textvariable=destination_path, width=50, state="disabled"
)
file_destination_input.grid(row=4, column=0, **default_options)
file_destination_browse_button = ttk.Button(
    window_step1,
    text="Parcourir",
    command=lambda: destination_path.set(filedialog.askdirectory()),
    state="disabled",
)
file_destination_browse_button.grid(row=4, column=1, **default_options)

next_step_button = ttk.Button(window_step1, text="Suivant", command=nextStep).grid(
    row=5, columnspan=3, **default_options
)

# Window 2 components
ttk.Label(window_step2, text="Nom du fichier:").grid(
    row=0, column=0, sticky=W, **default_options
)
info_file_name_variable = tk.StringVar()
ttk.Label(window_step2, textvariable=info_file_name_variable).grid(
    row=0, column=1, sticky=W, **default_options
)

ttk.Label(window_step2, text="FPS:").grid(row=1, column=0, sticky=W, **default_options)
info_fps_variable = tk.StringVar()
ttk.Label(window_step2, textvariable=info_fps_variable).grid(
    row=1, column=1, sticky=W, **default_options
)

ttk.Label(window_step2, text="Durée:").grid(
    row=2, column=0, sticky=W, **default_options
)
info_duree_variable = tk.StringVar()
ttk.Label(window_step2, textvariable=info_duree_variable).grid(
    row=2, column=1, sticky=W, **default_options
)

ttk.Label(window_step2, text="Temps de début (s):").grid(
    row=3, column=0, sticky=W, **default_options
)
start_time = tk.StringVar()
start_time_entry = ttk.Entry(window_step2, textvariable=start_time, width=4)
start_time_entry.grid(row=3, column=1, sticky=W, **default_options)

ttk.Label(window_step2, text="Temps de fin (s):").grid(
    row=4, column=0, sticky=W, **default_options
)
end_time = tk.StringVar()
end_time_entry = ttk.Entry(window_step2, textvariable=end_time, width=4)
end_time_entry.grid(row=4, column=1, sticky=W, **default_options)

progressbar = ttk.Progressbar(window_step2, length=250, mode="determinate")
progressbar.grid(row=5, columnspan=3, **default_options)
progress_label = tk.StringVar()
ttk.Label(window_step2, textvariable=progress_label).grid(row=6, columnspan=3)

previous_step_button = ttk.Button(window_step2, text="Précédent", command=previousStep)
previous_step_button.grid(row=7, column=0, **default_options)
start_extraction_button = ttk.Button(
    window_step2, text="Extraire", command=runExtraction
)
start_extraction_button.grid(row=7, column=1, **default_options)

stop_extraction_button = ttk.Button(
    window_step2, text="Arrêter", command=stopExtraction
)

window_step1.grid(padx=10, pady=10)


def on_closing():
    global in_progress, cap

    if in_progress:
        stopExtraction()

    if cap and cap.isOpened():
        cap.release()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
