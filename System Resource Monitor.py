import tkinter as tk
from tkinter import ttk
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time

class SystemMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("System Resource Monitor")
        self.root.geometry("1200x800")
        
        # Set up frames
        self.info_frame = ttk.LabelFrame(self.root, text="System Information")
        self.info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.graph_frame = ttk.LabelFrame(self.root, text="Real-Time Graphs")
        self.graph_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.process_frame = ttk.LabelFrame(self.root, text="Top Processes")
        self.process_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.partition_frame = ttk.LabelFrame(self.root, text="Disk Partitions")
        self.partition_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # CPU, Memory, Disk, Network, Battery, GPU Labels
        self.cpu_label = ttk.Label(self.info_frame, text="CPU Usage: ", font=("Helvetica", 12))
        self.cpu_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        
        self.memory_label = ttk.Label(self.info_frame, text="Memory Usage: ", font=("Helvetica", 12))
        self.memory_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        
        self.disk_label = ttk.Label(self.info_frame, text="Disk Usage: ", font=("Helvetica", 12))
        self.disk_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        
        self.network_label = ttk.Label(self.info_frame, text="Network Usage (Down/Up): ", font=("Helvetica", 12))
        self.network_label.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        
        self.temp_label = ttk.Label(self.info_frame, text="CPU Temperature: ", font=("Helvetica", 12))
        self.temp_label.grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
        
        self.battery_label = ttk.Label(self.info_frame, text="Battery Status: ", font=("Helvetica", 12))
        self.battery_label.grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)
        
        self.gpu_label = ttk.Label(self.info_frame, text="GPU Usage: ", font=("Helvetica", 12))
        self.gpu_label.grid(row=6, column=0, padx=10, pady=10, sticky=tk.W)
        
        # Initialize matplotlib figures for CPU, Memory, Disk, and Network graphs
        self.fig, (self.ax1, self.ax2, self.ax3, self.ax4) = plt.subplots(4, 1, figsize=(10, 12))
        self.fig.tight_layout(pad=3)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        self.cpu_usage_data = []
        self.memory_usage_data = []
        self.disk_usage_data = []
        self.network_down_data = []
        self.network_up_data = []
        
        # Listbox for displaying top processes
        self.process_listbox = tk.Listbox(self.process_frame, height=10, font=("Helvetica", 12))
        self.process_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Listbox for disk partitions
        self.partition_listbox = tk.Listbox(self.partition_frame, height=5, font=("Helvetica", 12))
        self.partition_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Start the update thread
        self.update_thread = threading.Thread(target=self.update_data)
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def update_data(self):
        last_net = psutil.net_io_counters()
        while True:
            # Gather system information
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            memory_usage = memory_info.percent
            disk_info = psutil.disk_usage('/')
            disk_usage = disk_info.percent
            net_info = psutil.net_io_counters()
            network_down = (net_info.bytes_recv - last_net.bytes_recv) / 1024 / 1024  # MB/s
            network_up = (net_info.bytes_sent - last_net.bytes_sent) / 1024 / 1024  # MB/s
            last_net = net_info
            
            # Update Labels
            self.cpu_label.config(text=f"CPU Usage: {cpu_usage}%")
            self.memory_label.config(text=f"Memory Usage: {memory_usage}%")
            self.disk_label.config(text=f"Disk Usage: {disk_usage}%")
            self.network_label.config(text=f"Network Usage: Down {network_down:.2f} MB/s, Up {network_up:.2f} MB/s")
            
            try:
                # Get CPU temperature (some systems may not support this)
                temp_info = psutil.sensors_temperatures().get('coretemp', [])[0]
                temp = temp_info.current if temp_info else None
                self.temp_label.config(text=f"CPU Temperature: {temp:.1f}°C" if temp else "CPU Temperature: N/A")
            except:
                self.temp_label.config(text="CPU Temperature: N/A")
            
            # Get battery status
            battery = psutil.sensors_battery()
            if battery:
                battery_status = f"{battery.percent}% {'Charging' if battery.power_plugged else 'Discharging'}"
                self.battery_label.config(text=f"Battery Status: {battery_status}")
            else:
                self.battery_label.config(text="Battery Status: N/A")
            
            # Get GPU usage (if available)
            try:
                gpu_info = psutil.sensors_temperatures().get('gpu', [])[0]  # Example placeholder, adjust for actual GPU monitoring
                gpu_usage = gpu_info.current if gpu_info else None
                self.gpu_label.config(text=f"GPU Usage: {gpu_usage}°C" if gpu_usage else "GPU Usage: N/A")
            except:
                self.gpu_label.config(text="GPU Usage: N/A")
            
            # Update graph data
            if len(self.cpu_usage_data) > 50:
                self.cpu_usage_data.pop(0)
                self.memory_usage_data.pop(0)
                self.disk_usage_data.pop(0)
                self.network_down_data.pop(0)
                self.network_up_data.pop(0)
            
            self.cpu_usage_data.append(cpu_usage)
            self.memory_usage_data.append(memory_usage)
            self.disk_usage_data.append(disk_usage)
            self.network_down_data.append(network_down)
            self.network_up_data.append(network_up)
            
            # Update the graphs
            self.ax1.clear()
            self.ax1.plot(self.cpu_usage_data, label="CPU Usage (%)", color="blue")
            self.ax1.set_ylim(0, 100)
            self.ax1.legend(loc="upper right")
            self.ax1.set_title("CPU Usage Over Time")
            
            self.ax2.clear()
            self.ax2.plot(self.memory_usage_data, label="Memory Usage (%)", color="green")
            self.ax2.set_ylim(0, 100)
            self.ax2.legend(loc="upper right")
            self.ax2.set_title("Memory Usage Over Time")
            
            self.ax3.clear()
            self.ax3.plot(self.disk_usage_data, label="Disk Usage (%)", color="orange")
            self.ax3.set_ylim(0, 100)
            self.ax3.legend(loc="upper right")
            self.ax3.set_title("Disk Usage Over Time")
            
            self.ax4.clear()
            self.ax4.plot(self.network_down_data, label="Network Download (MB/s)", color="red")
            self.ax4.plot(self.network_up_data, label="Network Upload (MB/s)", color="purple")
            self.ax4.legend(loc="upper right")
            self.ax4.set_title("Network Usage Over Time")
            
            self.canvas.draw()
            
            # Update the process listbox
            self.update_process_listbox()
            
            # Update the partition listbox
            self.update_partition_listbox()
            
            # Check for high usage alarms
            self.check_for_alarms(cpu_usage, memory_usage, disk_usage)
            
            time.sleep(1)
    
    def update_process_listbox(self):
        # Clear the listbox
        self.process_listbox.delete(0, tk.END)
        
        # Get the top 5 processes by CPU usage
        processes = [(p.info['cpu_percent'], p.info['name']) for p in psutil.process_iter(['name', 'cpu_percent'])]
        top_processes = sorted(processes, key=lambda x: x[0], reverse=True)[:5]
        
        for cpu_percent, name in top_processes:
            self.process_listbox.insert(tk.END, f"{name}: {cpu_percent}% CPU")
    
    def update_partition_listbox(self):
        # Clear the listbox
        self.partition_listbox.delete(0, tk.END)
        
        # Get all disk partitions and their usage
        partitions = psutil.disk_partitions()
        for partition in partitions:
            usage = psutil.disk_usage(partition.mountpoint)
            self.partition_listbox.insert(tk.END, f"{partition.device}: {usage.percent}% used")
    
    def check_for_alarms(self, cpu_usage, memory_usage, disk_usage):
        if cpu_usage > 90:
            self.show_alarm("CPU usage is over 90%!")
        if memory_usage > 90:
            self.show_alarm("Memory usage is over 90%!")
        if disk_usage > 90:
            self.show_alarm("Disk usage is over 90%!")
    
    def show_alarm(self, message):
        alarm_window = tk.Toplevel(self.root)
        alarm_window.title("Alarm")
        alarm_label = ttk.Label(alarm_window, text=message, font=("Helvetica", 14))
        alarm_label.pack(padx=20, pady=20)
        ok_button = ttk.Button(alarm_window, text="OK", command=alarm_window.destroy)
        ok_button.pack(pady=10)

# Run the application
root = tk.Tk()
app = SystemMonitor(root)
root.mainloop()
