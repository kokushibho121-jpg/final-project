import csv
import datetime as dt
import tkinter as tk
from tkinter import filedialog

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from .monitor import Monitor


class App:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("AI Memory Leak and Resource Anomaly Detection Platform")
        self.root.geometry("1320x780")
        self.root.configure(bg="#0b1d3a")

        self.monitor = Monitor()
        self.after_id = None
        self.threshold = 500.0
        self.history_limit = 70
        self.was_warning = False

        self.times = []
        self.memory_values = []
        self.cpu_values = []
        self.alert_times = []
        self.alert_memory = []
        self.logs = []

        self.memory_text = tk.StringVar(value="0 MB")
        self.cpu_text = tk.StringVar(value="0 %")
        self.risk_text = tk.StringVar(value="0 %")
        self.health_text = tk.StringVar(value="100 %")
        self.status_text = tk.StringVar(value="System Stable")
        self.threshold_text = tk.StringVar(value="500")

        self.build_ui()
        self.seed_graph()

    def build_ui(self) -> None:
        main = tk.Frame(self.root, bg="#0b1d3a")
        main.pack(fill="both", expand=True, padx=20, pady=18)

        tk.Label(
            main,
            text="AI Powered Memory Leak Detection Platform",
            font=("Arial", 32, "bold"),
            bg="#0b1d3a",
            fg="white",
        ).pack(pady=(10, 22))

        cards = tk.Frame(main, bg="#0b1d3a")
        cards.pack(fill="x")

        self.create_card(cards, "Memory Usage", self.memory_text, "#3aa7ff").pack(side="left", fill="x", expand=True, padx=8)
        self.create_card(cards, "CPU Usage", self.cpu_text, "#ff9d3d").pack(side="left", fill="x", expand=True, padx=8)
        self.create_card(cards, "Leak Risk", self.risk_text, "#ffd84d").pack(side="left", fill="x", expand=True, padx=8)
        self.create_card(cards, "System Health", self.health_text, "#38d66b").pack(side="left", fill="x", expand=True, padx=8)

        controls = tk.Frame(main, bg="#0b1d3a")
        controls.pack(pady=18)

        tk.Label(
            controls,
            text="Memory Threshold:",
            font=("Arial", 18),
            bg="#0b1d3a",
            fg="white",
        ).pack(side="left", padx=(0, 10))

        tk.Entry(controls, textvariable=self.threshold_text, width=8, justify="center", font=("Arial", 16)).pack(
            side="left", padx=(0, 12)
        )

        self.create_button(controls, "Set", self.set_threshold).pack(side="left", padx=6)
        self.create_button(controls, "Export Logs", self.export_logs).pack(side="left", padx=6)
        self.create_button(controls, "Start", self.start).pack(side="left", padx=6)
        self.create_button(controls, "Stop", self.stop).pack(side="left", padx=6)

        graph_box = tk.Frame(main, bg="#15284d", bd=0)
        graph_box.pack(fill="both", expand=True, pady=(4, 0))

        tk.Label(
            graph_box,
            text="Resource Usage Over Time",
            font=("Arial", 20),
            bg="#15284d",
            fg="white",
        ).pack(pady=18)

        self.figure = Figure(figsize=(11.5, 5.2), dpi=100)
        self.figure.patch.set_facecolor("#213459")

        self.memory_axis = self.figure.add_subplot(111)
        self.cpu_axis = self.memory_axis.twinx()

        self.memory_axis.set_facecolor("#243759")
        self.memory_axis.grid(True, linestyle="--", alpha=0.20, color="#9eb2d4")
        self.memory_axis.set_xlabel("Time", color="white", fontsize=14)
        self.memory_axis.set_ylabel("Memory (MB)", color="white", fontsize=14)
        self.cpu_axis.set_ylabel("CPU (%)", color="white", fontsize=14)
        self.cpu_axis.set_ylim(0, 100)

        self.memory_axis.tick_params(axis="x", colors="#d6dff0")
        self.memory_axis.tick_params(axis="y", colors="#d6dff0")
        self.cpu_axis.tick_params(axis="y", colors="#d6dff0")

        for spine in self.memory_axis.spines.values():
            spine.set_color("#8ea5c8")
        for spine in self.cpu_axis.spines.values():
            spine.set_color("#8ea5c8")

        self.memory_line, = self.memory_axis.plot([], [], color="#3aa7ff", linewidth=2.5)
        self.cpu_line, = self.cpu_axis.plot([], [], color="#ff9238", linewidth=2.5)
        self.alert_scatter = self.memory_axis.scatter([], [], color="#ff5a66", s=70, marker="x")

        self.figure.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.figure, master=graph_box)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=16, pady=(0, 18))

        self.status_label = tk.Label(
            main,
            textvariable=self.status_text,
            font=("Arial", 30, "bold"),
            bg="#0b1d3a",
            fg="#38d66b",
        )
        self.status_label.pack(pady=16)

        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def create_card(self, parent: tk.Frame, title: str, value_var: tk.StringVar, color: str) -> tk.Frame:
        card = tk.Frame(parent, bg="#22365a", width=300, height=170)
        card.pack_propagate(False)

        tk.Label(card, text=title, font=("Arial", 18), bg="#22365a", fg="#d3ddf2").pack(pady=(28, 10))
        tk.Label(card, textvariable=value_var, font=("Arial", 36, "bold"), bg="#22365a", fg=color).pack()
        return card

    def create_button(self, parent: tk.Frame, text: str, command) -> tk.Button:
        return tk.Button(parent, text=text, width=10, height=1, font=("Arial", 15, "bold"), command=command)

    def seed_graph(self) -> None:
        # Fill the graph once so the dashboard does not look empty at the start.
        for _ in range(18):
            data = self.monitor.next_data(self.threshold)
            self.add_history(data)
        self.update_cards(data)
        self.redraw_graph()

    def read_threshold(self) -> float:
        try:
            value = float(self.threshold_text.get())
            if value > 0:
                return value
        except ValueError:
            pass
        self.threshold_text.set(str(int(self.threshold)))
        return self.threshold

    def set_threshold(self) -> None:
        self.threshold = self.read_threshold()
        self.status_text.set(f"Threshold Set: {self.threshold:.0f} MB")
        self.status_label.config(fg="#ffd84d")

    def start(self) -> None:
        self.stop()
        self.threshold = self.read_threshold()
        self.update_loop()

    def stop(self) -> None:
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.status_text.set("System Stopped")
        self.status_label.config(fg="#d6dff0")

    def update_loop(self) -> None:
        data = self.monitor.next_data(self.threshold)
        self.add_history(data)
        self.update_cards(data)

        warning_now = data.leak
        if warning_now:
            self.status_text.set("System Warning")
            self.status_label.config(fg="#ff6d5c")
            if not self.was_warning:
                self.alert_times.append(data.second)
                self.alert_memory.append(data.memory_mb)
                self.logs.append(
                    {
                        "time": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "memory_mb": f"{data.memory_mb:.2f}",
                        "cpu_percent": f"{data.cpu_percent:.2f}",
                        "score_percent": str(data.score),
                        "threshold_mb": f"{self.threshold:.0f}",
                        "status": "Leak Detected",
                    }
                )
        else:
            self.status_text.set("System Stable")
            self.status_label.config(fg="#38d66b")

        self.was_warning = warning_now
        self.redraw_graph()
        self.after_id = self.root.after(1000, self.update_loop)

    def update_cards(self, data) -> None:
        health = max(0, 100 - data.score)
        self.memory_text.set(f"{data.memory_mb:.0f} MB")
        self.cpu_text.set(f"{data.cpu_percent:.0f} %")
        self.risk_text.set(f"{data.score} %")
        self.health_text.set(f"{health} %")

    def add_history(self, data) -> None:
        self.times.append(data.second)
        self.memory_values.append(data.memory_mb)
        self.cpu_values.append(data.cpu_percent)

        if len(self.times) > self.history_limit:
            self.times.pop(0)
            self.memory_values.pop(0)
            self.cpu_values.pop(0)

    def redraw_graph(self) -> None:
        if not self.times:
            return

        # Update both graph lines using the latest history lists.
        self.memory_line.set_data(self.times, self.memory_values)
        self.cpu_line.set_data(self.times, self.cpu_values)

        if self.alert_times:
            self.alert_scatter.set_offsets(list(zip(self.alert_times, self.alert_memory)))
            self.alert_scatter.set_visible(True)
        else:
            self.alert_scatter.set_offsets([[0.0, 0.0]])
            self.alert_scatter.set_visible(False)

        self.memory_axis.set_xlim(self.times[0], max(self.times[-1], self.times[0] + 1))

        minimum = min(self.memory_values)
        maximum = max(self.memory_values)
        padding = max(10.0, (maximum - minimum) * 0.25)
        self.memory_axis.set_ylim(minimum - padding, maximum + padding)

        self.canvas.draw_idle()

    def export_logs(self) -> None:
        if not self.logs:
            self.status_text.set("No Logs To Export")
            self.status_label.config(fg="#ffd84d")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save logs",
            defaultextension=".csv",
            initialfile=f"anomaly_logs_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not file_path:
            return

        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["time", "memory_mb", "cpu_percent", "score_percent", "threshold_mb", "status"],
            )
            writer.writeheader()
            writer.writerows(self.logs)

        self.status_text.set("Logs Exported")
        self.status_label.config(fg="#d6dff0")

    def close(self) -> None:
        self.stop()
        self.monitor.close()
        self.root.destroy()


def run_app() -> None:
    App().root.mainloop()
