from tkinter import *
from tkinter import ttk, messagebox, filedialog
import speedtest
import threading
import csv
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# Global variables
history = []

# Function to perform the speed test
def speedcheck():
    def run_speedtest():
        button.config(state=DISABLED, text="Testing...")  # Disable button during test
        progress_bar.start()  # Start the progress bar

        st = speedtest.Speedtest()
        
        # Server selection
        if server_var.get() != "Auto":
            st.get_servers([server_var.get()])
        else:
            st.get_best_server()  # Find the best server automatically

        # Measure ping
        ping = round(st.results.ping, 2)
        lab_ping.config(text=f"{ping} ms")

        # Measure download speed
        download_speed = round(st.download() / 10**6, 2)  # Convert to Mbps
        lab_down.config(text=f"{download_speed} Mbps")

        # Measure upload speed
        upload_speed = round(st.upload() / 10**6, 2)  # Convert to Mbps
        lab_up.config(text=f"{upload_speed} Mbps")

        # Update history
        history.append((ping, download_speed, upload_speed))
        update_history_log()

        # Update graph
        update_graph()

        # Display speed rating
        display_speed_rating(download_speed, upload_speed)

        # Stop the progress bar and re-enable the button
        progress_bar.stop()
        button.config(state=NORMAL, text="Check Speed")

    # Run the speed test in a separate thread to avoid freezing the UI
    threading.Thread(target=run_speedtest).start()

# Function to display speed rating
def display_speed_rating(download_speed, upload_speed):
    if download_speed > 50 and upload_speed > 10:
        rating = "Excellent"
        color = "#A3BE8C"  # Green
    elif download_speed > 25 and upload_speed > 5:
        rating = "Good"
        color = "#EBCB8B"  # Yellow
    elif download_speed > 10 and upload_speed > 2:
        rating = "Better"
        color = "#D08770"  # Orange
    else:
        rating = "Medium"
        color = "#BF616A"  # Red

    lab_rating.config(text=f"Rating: {rating}", fg=color)

# Function to update the history log
def update_history_log():
    history_text.config(state=NORMAL)
    history_text.delete(1.0, END)
    for i, (ping, down, up) in enumerate(history, 1):
        history_text.insert(END, f"Test {i}: Ping = {ping} ms, Download = {down} Mbps, Upload = {up} Mbps\n")
    history_text.config(state=DISABLED)

# Function to update the graph
def update_graph():
    if not history:
        return

    # Clear the previous graph
    ax.clear()

    # Plot the data
    pings = [x[0] for x in history]
    downloads = [x[1] for x in history]
    uploads = [x[2] for x in history]

    ax.plot(pings, label="Ping (ms)", marker="o", color="#88C0D0")
    ax.plot(downloads, label="Download (Mbps)", marker="o", color="#A3BE8C")
    ax.plot(uploads, label="Upload (Mbps)", marker="o", color="#EBCB8B")

    ax.set_xlabel("Test Number")
    ax.set_ylabel("Speed")
    ax.set_title("Speed Test History")
    ax.legend()
    ax.set_facecolor("#3B4252")
    fig.patch.set_facecolor("#3B4252")

    # Draw the graph on the canvas
    canvas.draw()

# Function to export results to a CSV file
def export_results():
    if not history:
        messagebox.showwarning("No Data", "No speed test data to export!")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if file_path:
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Test Number", "Ping (ms)", "Download (Mbps)", "Upload (Mbps)"])
            for i, (ping, down, up) in enumerate(history, 1):
                writer.writerow([i, ping, down, up])
        messagebox.showinfo("Export Successful", f"Results exported to {file_path}")

# Function to clear history
def clear_history():
    global history
    history = []
    update_history_log()
    ax.clear()
    canvas.draw()
    lab_rating.config(text="Rating: N/A", fg="#D8DEE9")

# Function to fetch server list dynamically
def fetch_servers():
    try:
        st = speedtest.Speedtest()
        servers = st.get_servers()
        server_list = ["Auto"]  # Default option
        for country, server_ids in servers.items():
            for server_id in server_ids:
                server_list.append(server_id)
        server_dropdown["values"] = server_list
    except speedtest.ConfigRetrievalError:
        # If server list cannot be fetched, default to "Auto"
        server_dropdown["values"] = ["Auto"]
        messagebox.showwarning("Server Error", "Unable to fetch server list. Defaulting to 'Auto'.")

# GUI Setup
sp = Tk()
sp.title("Internet Speed Test")
sp.geometry("1200x800")
sp.config(bg="#2E3440")  # Dark background color

# Custom Fonts
title_font = ("Helvetica", 24, "bold")
label_font = ("Helvetica", 14)
result_font = ("Helvetica", 16, "bold")

# Left Frame (Labels and History Log)
left_frame = Frame(sp, bg="#2E3440")
left_frame.pack(side=LEFT, fill=Y, padx=20, pady=20)

# Title Label
lab_title = Label(left_frame, text="Internet Speed Test", font=title_font, bg="#2E3440", fg="#D8DEE9")
lab_title.pack(pady=20)

# Server Selection
server_var = StringVar(value="Auto")
server_label = Label(left_frame, text="Select Server:", font=label_font, bg="#2E3440", fg="#D8DEE9")
server_label.pack(pady=10)

server_dropdown = ttk.Combobox(left_frame, textvariable=server_var, font=label_font, state="readonly")
server_dropdown.pack(pady=10)

# Fetch servers dynamically
fetch_servers()

# Ping Label
lab_ping_text = Label(left_frame, text="Ping:", font=label_font, bg="#2E3440", fg="#D8DEE9")
lab_ping_text.pack(pady=10)

lab_ping = Label(left_frame, text="00 ms", font=result_font, bg="#2E3440", fg="#88C0D0")
lab_ping.pack(pady=10)

# Download Speed Label
lab_down_text = Label(left_frame, text="Download Speed:", font=label_font, bg="#2E3440", fg="#D8DEE9")
lab_down_text.pack(pady=10)

lab_down = Label(left_frame, text="00 Mbps", font=result_font, bg="#2E3440", fg="#A3BE8C")
lab_down.pack(pady=10)

# Upload Speed Label
lab_up_text = Label(left_frame, text="Upload Speed:", font=label_font, bg="#2E3440", fg="#D8DEE9")
lab_up_text.pack(pady=10)

lab_up = Label(left_frame, text="00 Mbps", font=result_font, bg="#2E3440", fg="#EBCB8B")
lab_up.pack(pady=10)

# Speed Rating Label
lab_rating = Label(left_frame, text="Rating: N/A", font=result_font, bg="#2E3440", fg="#D8DEE9")
lab_rating.pack(pady=10)

# Progress Bar
progress_bar = ttk.Progressbar(left_frame, orient=HORIZONTAL, length=400, mode="indeterminate")
progress_bar.pack(pady=20)

# Check Speed Button
button = Button(left_frame, text="Check Speed", font=label_font, bg="#5E81AC", fg="#D8DEE9", command=speedcheck)
button.pack(pady=10)

# Export Button
export_button = Button(left_frame, text="Export Results", font=label_font, bg="#5E81AC", fg="#D8DEE9", command=export_results)
export_button.pack(pady=10)

# Clear History Button
clear_button = Button(left_frame, text="Clear History", font=label_font, bg="#5E81AC", fg="#D8DEE9", command=clear_history)
clear_button.pack(pady=10)

# History Log
history_label = Label(left_frame, text="History Log:", font=label_font, bg="#2E3440", fg="#D8DEE9")
history_label.pack(pady=10)

history_text = Text(left_frame, height=10, width=50, font=label_font, bg="#3B4252", fg="#D8DEE9", state=DISABLED)
history_text.pack(pady=10)

# Right Frame (Graphical Representation)
right_frame = Frame(sp, bg="#2E3440")
right_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=20, pady=20)

# Graph
fig = Figure(figsize=(6, 4), facecolor="#3B4252")
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=right_frame)
canvas.get_tk_widget().pack(fill=BOTH, expand=True)

# Start the main loop
sp.mainloop()