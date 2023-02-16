import nidaqmx
import tkinter as tk
import numpy as np
import queue
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.animation as animation


class TaskThread(threading.Thread):
    def __init__(self, task, queue, num_points, interval):
        threading.Thread.__init__(self)
        self.task = task
        self.queue = queue
        self.num_points = num_points
        self.interval = interval
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            if not self.task.is_task_done():
                voltage_data = np.array(self.task.read(self.num_points, timeout=self.interval))
                self.queue.put(voltage_data)
            time.sleep(0)

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

class App:
    def __init__(self, root, task, num_points, interval):
        self.task = task
        self.num_points = num_points
        self.interval = interval

        self.queue = queue.Queue(maxsize=1)

        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim([0, num_points])
        self.ax.set_ylim([-1, 1])
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Voltage")
        self.line, = self.ax.plot([], [], color="red")

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.toolbar = NavigationToolbar2Tk(self.canvas, root)
        self.toolbar.update()

        self.exit_button = tk.Button(root, text="Exit", command=self.on_close)
        self.exit_button.pack(side=tk.BOTTOM, padx=10, pady=10)

        self.thread = TaskThread(self.task, self.queue, self.num_points, self.interval)
        self.thread.start()
        self.anim = animation.FuncAnimation(self.fig, self.animate, frames=None, interval=self.interval, save_count=100)

    def animate(self, frame):
        try:
            voltage_data = self.queue.get(timeout=100)
        except queue.Empty:
            voltage_data = np.zeros(self.num_points)

        voltage_data_scaled = (voltage_data - 1.315) * 0.8949
        x_coords = np.arange(self.num_points)

        self.line.set_data(x_coords, voltage_data_scaled)
        self.ax.draw_artist(self.ax.patch)
        self.ax.draw_artist(self.line)

        self.canvas.blit(self.ax.bbox)
        self.canvas.flush_events()

    def on_close(self):
        self.thread.stop()
        plt.close(self.fig)
        root.quit()


if __name__ == "__main__":
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan("AI/ai1")

        root = tk.Tk()
        root.title("NI 9215 AI/ai1 Continuous Signal Display")

        app = App(root, task, num_points=800, interval=0.1)

        root.protocol("WM_DELETE_WINDOW", app.on_close)
        root.mainloop()
