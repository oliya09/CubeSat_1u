#!/usr/bin/env python3
"""
Telemetry Viewer for Ground Station
"""
import time 
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime
import threading

class TelemetryViewer:
    """Telemetry data viewer with plots"""
    
    def __init__(self, parent, ground_station):
        self.parent = parent
        self.gs = ground_station
        
        # Data storage for plots
        self.time_data = []
        self.temp_data = []
        self.pressure_data = []
        self.humidity_data = []
        self.radiation_data = []
        self.battery_data = []
        self.mag_x_data = []
        self.mag_y_data = []
        self.mag_z_data = []
        self.corrosion_data = []
        
        self.max_points = 1000
        
        # Setup GUI
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the telemetry viewer GUI"""
        # Create paned window for resizable sections
        self.paned = ttk.PanedWindow(self.parent, orient=tk.HORIZONTAL)
        self.paned.pack(fill='both', expand=True)
        
        # Left panel - Current values
        left_frame = ttk.Frame(self.paned)
        self.paned.add(left_frame, weight=1)
        
        # Current values display
        self.setup_current_values(left_frame)
        
        # Right panel - Plots
        right_frame = ttk.Frame(self.paned)
        self.paned.add(right_frame, weight=3)
        
        # Create notebook for plot tabs
        plot_notebook = ttk.Notebook(right_frame)
        plot_notebook.pack(fill='both', expand=True)
        
        # Temperature plot
        temp_frame = ttk.Frame(plot_notebook)
        plot_notebook.add(temp_frame, text="Temperature")
        self.setup_temp_plot(temp_frame)
        
        # Radiation plot
        rad_frame = ttk.Frame(plot_notebook)
        plot_notebook.add(rad_frame, text="Radiation")
        self.setup_rad_plot(rad_frame)
        
        # Magnetometer plot
        mag_frame = ttk.Frame(plot_notebook)
        plot_notebook.add(mag_frame, text="Magnetometer")
        self.setup_mag_plot(mag_frame)
        
        # Environment plot
        env_frame = ttk.Frame(plot_notebook)
        plot_notebook.add(env_frame, text="Environment")
        self.setup_env_plot(env_frame)
        
        # Battery plot
        bat_frame = ttk.Frame(plot_notebook)
        plot_notebook.add(bat_frame, text="Battery")
        self.setup_battery_plot(bat_frame)
        
    def setup_current_values(self, parent):
        """Setup current values display"""
        # Create canvas with scrollbar
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title
        title = ttk.Label(scrollable_frame, text="Current Telemetry", 
                         font=('Arial', 14, 'bold'))
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Create labels for each telemetry value
        self.value_labels = {}
        telemetry_items = [
            ("Timestamp", "timestamp_str"),
            ("System State", "system_state"),
            ("Battery Voltage", "battery_voltage", "{:.2f} V"),
            ("Battery Current", "battery_current", "{:.2f} mA"),
            ("Temperature (BME)", "temperature_bme", "{:.2f} °C"),
            ("Temperature (TMP)", "temperature_tmp", "{:.2f} °C"),
            ("Pressure", "pressure", "{:.2f} hPa"),
            ("Humidity", "humidity", "{:.2f} %"),
            ("Radiation", "radiation_cps", "{:.0f} CPS"),
            ("Mag X", "mag_x", "{:.3f} G"),
            ("Mag Y", "mag_y", "{:.3f} G"),
            ("Mag Z", "mag_z", "{:.3f} G"),
            ("Corrosion Raw", "corrosion_raw", "{:d}"),
            ("Sequence", "sequence", "{:d}"),
            ("Uptime", "uptime", "{:d} s"),
            ("Error Flags", "error_flags", "0x{:02X}")
        ]
        
        for i, item in enumerate(telemetry_items):
            label_text = item[0]
            key = item[1]
            format_str = item[2] if len(item) > 2 else "{}"
            
            # Label
            ttk.Label(scrollable_frame, text=f"{label_text}:", 
                     font=('Arial', 10, 'bold')).grid(
                row=i+1, column=0, sticky='w', padx=5, pady=2
            )
            
            # Value
            value_label = ttk.Label(scrollable_frame, text="---", 
                                   font=('Courier', 10))
            value_label.grid(row=i+1, column=1, sticky='w', padx=5, pady=2)
            
            self.value_labels[key] = (value_label, format_str)
            
        # Add warning indicators
        ttk.Separator(scrollable_frame, orient='horizontal').grid(
            row=len(telemetry_items)+1, column=0, columnspan=2, sticky='ew', pady=10
        )
        
        ttk.Label(scrollable_frame, text="Warnings:", 
                 font=('Arial', 12, 'bold')).grid(
            row=len(telemetry_items)+2, column=0, columnspan=2, pady=5
        )
        
        self.warning_label = ttk.Label(scrollable_frame, text="None", 
                                      foreground='green')
        self.warning_label.grid(row=len(telemetry_items)+3, column=0, 
                               columnspan=2, pady=5)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def setup_temp_plot(self, parent):
        """Setup temperature plot"""
        self.temp_fig = Figure(figsize=(6, 4), dpi=100)
        self.temp_ax = self.temp_fig.add_subplot(111)
        self.temp_line, = self.temp_ax.plot([], [], 'r-', label='BME280')
        self.tmp_line, = self.temp_ax.plot([], [], 'b-', label='TMP117')
        
        self.temp_ax.set_xlabel('Time (s)')
        self.temp_ax.set_ylabel('Temperature (°C)')
        self.temp_ax.set_title('Temperature History')
        self.temp_ax.grid(True)
        self.temp_ax.legend()
        
        self.temp_canvas = FigureCanvasTkAgg(self.temp_fig, master=parent)
        self.temp_canvas.get_tk_widget().pack(fill='both', expand=True)
        
    def setup_rad_plot(self, parent):
        """Setup radiation plot"""
        self.rad_fig = Figure(figsize=(6, 4), dpi=100)
        self.rad_ax = self.rad_fig.add_subplot(111)
        self.rad_line, = self.rad_ax.plot([], [], 'g-')
        
        self.rad_ax.set_xlabel('Time (s)')
        self.rad_ax.set_ylabel('Counts per second')
        self.rad_ax.set_title('Radiation History')
        self.rad_ax.grid(True)
        
        self.rad_canvas = FigureCanvasTkAgg(self.rad_fig, master=parent)
        self.rad_canvas.get_tk_widget().pack(fill='both', expand=True)
        
    def setup_mag_plot(self, parent):
        """Setup magnetometer plot"""
        self.mag_fig = Figure(figsize=(6, 4), dpi=100)
        self.mag_ax = self.mag_fig.add_subplot(111)
        
        self.mag_x_line, = self.mag_ax.plot([], [], 'r-', label='X')
        self.mag_y_line, = self.mag_ax.plot([], [], 'g-', label='Y')
        self.mag_z_line, = self.mag_ax.plot([], [], 'b-', label='Z')
        
        self.mag_ax.set_xlabel('Time (s)')
        self.mag_ax.set_ylabel('Magnetic Field (Gauss)')
        self.mag_ax.set_title('Magnetometer History')
        self.mag_ax.grid(True)
        self.mag_ax.legend()
        
        self.mag_canvas = FigureCanvasTkAgg(self.mag_fig, master=parent)
        self.mag_canvas.get_tk_widget().pack(fill='both', expand=True)
        
    def setup_env_plot(self, parent):
        """Setup environment plot (pressure, humidity)"""
        self.env_fig = Figure(figsize=(6, 4), dpi=100)
        
        # Pressure subplot
        self.press_ax = self.env_fig.add_subplot(211)
        self.press_line, = self.press_ax.plot([], [], 'b-')
        self.press_ax.set_ylabel('Pressure (hPa)')
        self.press_ax.grid(True)
        
        # Humidity subplot
        self.hum_ax = self.env_fig.add_subplot(212)
        self.hum_line, = self.hum_ax.plot([], [], 'g-')
        self.hum_ax.set_xlabel('Time (s)')
        self.hum_ax.set_ylabel('Humidity (%)')
        self.hum_ax.grid(True)
        
        self.env_fig.tight_layout()
        
        self.env_canvas = FigureCanvasTkAgg(self.env_fig, master=parent)
        self.env_canvas.get_tk_widget().pack(fill='both', expand=True)
        
    def setup_battery_plot(self, parent):
        """Setup battery plot"""
        self.bat_fig = Figure(figsize=(6, 4), dpi=100)
        self.bat_ax = self.bat_fig.add_subplot(111)
        self.bat_line, = self.bat_ax.plot([], [], 'm-')
        
        self.bat_ax.set_xlabel('Time (s)')
        self.bat_ax.set_ylabel('Voltage (V)')
        self.bat_ax.set_title('Battery Voltage History')
        self.bat_ax.grid(True)
        
        # Add threshold lines
        self.bat_ax.axhline(y=3.7, color='g', linestyle='--', alpha=0.5, label='Nominal')
        self.bat_ax.axhline(y=3.5, color='y', linestyle='--', alpha=0.5, label='Low')
        self.bat_ax.axhline(y=3.4, color='r', linestyle='--', alpha=0.5, label='Critical')
        self.bat_ax.legend()
        
        self.bat_canvas = FigureCanvasTkAgg(self.bat_fig, master=parent)
        self.bat_canvas.get_tk_widget().pack(fill='both', expand=True)
        
    def update_telemetry(self, telemetry):
        """Update display with new telemetry"""
        # Update current values
        for key, (label, format_str) in self.value_labels.items():
            if key in telemetry:
                try:
                    value = telemetry[key]
                    if key == 'battery_voltage':
                        value = value / 1000.0  # Convert mV to V
                    elif key == 'timestamp_str':
                        value = datetime.now().strftime('%H:%M:%S')
                    elif key == 'system_state':
                        states = ['BOOT', 'IDLE', 'NOMINAL', 'SAFE', 'LOW_POWER', 'EMERGENCY']
                        value = states[value] if value < len(states) else f"UNKNOWN({value})"
                        
                    label.config(text=format_str.format(value))
                except:
                    label.config(text="ERR")
                    
        # Check for warnings
        warnings = []
        
        if telemetry.get('battery_voltage', 4000) < 3500:
            warnings.append("Low Battery!")
        if telemetry.get('temperature_bme', 20) > 60:
            warnings.append("High Temperature!")
        if telemetry.get('error_flags', 0) != 0:
            warnings.append("Error Flags Set!")
            
        if warnings:
            self.warning_label.config(text=", ".join(warnings), foreground='red')
        else:
            self.warning_label.config(text="None", foreground='green')
            
        # Update data arrays for plots
        current_time = time.time()
        self.time_data.append(current_time)
        
        self.temp_data.append(telemetry.get('temperature_bme', 0))
        self.pressure_data.append(telemetry.get('pressure', 0))
        self.humidity_data.append(telemetry.get('humidity', 0))
        self.radiation_data.append(telemetry.get('radiation_cps', 0))
        self.battery_data.append(telemetry.get('battery_voltage', 4000) / 1000.0)
        self.mag_x_data.append(telemetry.get('mag_x', 0))
        self.mag_y_data.append(telemetry.get('mag_y', 0))
        self.mag_z_data.append(telemetry.get('mag_z', 0))
        self.corrosion_data.append(telemetry.get('corrosion_raw', 0))
        
        # Limit data points
        if len(self.time_data) > self.max_points:
            self.time_data = self.time_data[-self.max_points:]
            self.temp_data = self.temp_data[-self.max_points:]
            self.pressure_data = self.pressure_data[-self.max_points:]
            self.humidity_data = self.humidity_data[-self.max_points:]
            self.radiation_data = self.radiation_data[-self.max_points:]
            self.battery_data = self.battery_data[-self.max_points:]
            self.mag_x_data = self.mag_x_data[-self.max_points:]
            self.mag_y_data = self.mag_y_data[-self.max_points:]
            self.mag_z_data = self.mag_z_data[-self.max_points:]
            self.corrosion_data = self.corrosion_data[-self.max_points:]
            
        # Update plots
        self.update_plots()
        
    def update_plots(self):
        """Update all plots"""
        if len(self.time_data) < 2:
            return
            
        # Normalize time to seconds from start
        t0 = self.time_data[0]
        t_norm = [t - t0 for t in self.time_data]
        
        # Temperature plot
        self.temp_line.set_data(t_norm, self.temp_data)
        self.temp_ax.relim()
        self.temp_ax.autoscale_view()
        self.temp_canvas.draw_idle()
        
        # Radiation plot
        self.rad_line.set_data(t_norm, self.radiation_data)
        self.rad_ax.relim()
        self.rad_ax.autoscale_view()
        self.rad_canvas.draw_idle()
        
        # Magnetometer plot
        self.mag_x_line.set_data(t_norm, self.mag_x_data)
        self.mag_y_line.set_data(t_norm, self.mag_y_data)
        self.mag_z_line.set_data(t_norm, self.mag_z_data)
        self.mag_ax.relim()
        self.mag_ax.autoscale_view()
        self.mag_canvas.draw_idle()
        
        # Environment plot
        self.press_line.set_data(t_norm, self.pressure_data)
        self.press_ax.relim()
        self.press_ax.autoscale_view()
        
        self.hum_line.set_data(t_norm, self.humidity_data)
        self.hum_ax.relim()
        self.hum_ax.autoscale_view()
        self.env_canvas.draw_idle()
        
        # Battery plot
        self.bat_line.set_data(t_norm, self.battery_data)
        self.bat_ax.relim()
        self.bat_ax.autoscale_view()
        self.bat_canvas.draw_idle()