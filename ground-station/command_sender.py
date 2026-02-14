#!/usr/bin/env python3
"""
Command Sender for Ground Station
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime
import json

class CommandSender:
    """Command sending interface"""
    
    def __init__(self, parent, ground_station):
        self.parent = parent
        self.gs = ground_station
        
        # Command history
        self.history = []
        
        # Setup GUI
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the command sender GUI"""
        # Command input frame
        input_frame = ttk.LabelFrame(self.parent, text="Send Command")
        input_frame.pack(fill='x', padx=5, pady=5)
        
        # Command type
        ttk.Label(input_frame, text="Command:").grid(row=0, column=0, padx=5, pady=5)
        
        self.command_var = tk.StringVar()
        commands = [
            "PING",
            "GET_TELEMETRY",
            "CAPTURE_IMAGE",
            "SET_MODE",
            "RESET",
            "TRANSMIT_FILE",
            "GET_STATUS",
            "SET_SCHEDULE",
            "BEACON"
        ]
        
        self.command_combo = ttk.Combobox(input_frame, textvariable=self.command_var,
                                         values=commands, width=20)
        self.command_combo.grid(row=0, column=1, padx=5, pady=5)
        self.command_combo.bind('<<ComboboxSelected>>', self.on_command_selected)
        
        # Parameters frame
        self.param_frame = ttk.Frame(input_frame)
        self.param_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
        
        # Send button
        ttk.Button(input_frame, text="Send Command", 
                  command=self.send_command).grid(row=2, column=0, columnspan=3, pady=10)
        
        # Quick commands frame
        quick_frame = ttk.LabelFrame(self.parent, text="Quick Commands")
        quick_frame.pack(fill='x', padx=5, pady=5)
        
        quick_buttons = [
            ("Ping", "PING"),
            ("Get Telemetry", "GET_TELEMETRY"),
            ("Capture Image", "CAPTURE_IMAGE"),
            ("Nominal Mode", ("SET_MODE", {"mode": 2})),
            ("Safe Mode", ("SET_MODE", {"mode": 3})),
            ("Beacon", "BEACON")
        ]
        
        for i, (label, cmd) in enumerate(quick_buttons):
            btn = ttk.Button(quick_frame, text=label,
                           command=lambda c=cmd: self.quick_command(c))
            btn.grid(row=i//3, column=i%3, padx=2, pady=2)
            
        # Command history
        history_frame = ttk.LabelFrame(self.parent, text="Command History")
        history_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.history_text = scrolledtext.ScrolledText(history_frame, height=15)
        self.history_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Bind double-click to re-send
        self.history_text.bind('<Double-Button-1>', self.resend_command)
        
    def on_command_selected(self, event):
        """Handle command selection"""
        # Clear parameter frame
        for widget in self.param_frame.winfo_children():
            widget.destroy()
            
        cmd = self.command_var.get()
        
        if cmd == "SET_MODE":
            ttk.Label(self.param_frame, text="Mode (0-5):").pack(side=tk.LEFT)
            self.mode_entry = ttk.Entry(self.param_frame, width=5)
            self.mode_entry.pack(side=tk.LEFT, padx=5)
            self.mode_entry.insert(0, "2")
            
        elif cmd == "TRANSMIT_FILE":
            ttk.Label(self.param_frame, text="Filename:").pack(side=tk.LEFT)
            self.file_entry = ttk.Entry(self.param_frame, width=30)
            self.file_entry.pack(side=tk.LEFT, padx=5)
            
        elif cmd == "SET_SCHEDULE":
            ttk.Label(self.param_frame, text="Interval (s):").pack(side=tk.LEFT)
            self.interval_entry = ttk.Entry(self.param_frame, width=10)
            self.interval_entry.pack(side=tk.LEFT, padx=5)
            self.interval_entry.insert(0, "600")
            
    def send_command(self):
        """Send the selected command"""
        cmd = self.command_var.get()
        
        if not cmd:
            return
            
        params = None
        
        if cmd == "SET_MODE" and hasattr(self, 'mode_entry'):
            try:
                mode = int(self.mode_entry.get())
                params = {"mode": mode}
            except:
                self.gs.log_message("Invalid mode value")
                return
                
        elif cmd == "TRANSMIT_FILE" and hasattr(self, 'file_entry'):
            filename = self.file_entry.get()
            if filename:
                params = {"filename": filename}
                
        elif cmd == "SET_SCHEDULE" and hasattr(self, 'interval_entry'):
            try:
                interval = int(self.interval_entry.get())
                params = {"interval": interval}
            except:
                self.gs.log_message("Invalid interval value")
                return
                
        self.execute_command(cmd, params)
        
    def quick_command(self, cmd):
        """Execute a quick command"""
        if isinstance(cmd, tuple):
            cmd_name, params = cmd
            self.execute_command(cmd_name, params)
        else:
            self.execute_command(cmd)
            
    def execute_command(self, cmd_name, params=None):
        """Execute a command"""
        # Map command names to IDs
        cmd_ids = {
            "PING": 0x01,
            "GET_TELEMETRY": 0x02,
            "CAPTURE_IMAGE": 0x03,
            "SET_MODE": 0x04,
            "RESET": 0x05,
            "TRANSMIT_FILE": 0x06,
            "GET_STATUS": 0x07,
            "SET_SCHEDULE": 0x08,
            "BEACON": 0x09
        }
        
        cmd_id = cmd_ids.get(cmd_name)
        if cmd_id is None:
            self.gs.log_message(f"Unknown command: {cmd_name}")
            return
            
        # Send command
        if self.gs.send_command(cmd_id, params):
            # Add to history
            timestamp = datetime.now().strftime('%H:%M:%S')
            cmd_str = f"[{timestamp}] {cmd_name}"
            if params:
                cmd_str += f" {json.dumps(params)}"
                
            self.history.append((timestamp, cmd_name, params))
            self.history_text.insert(tk.END, cmd_str + '\n')
            self.history_text.see(tk.END)
            
    def resend_command(self, event):
        """Resend a command from history"""
        try:
            # Get selected line
            index = self.history_text.index(tk.CURRENT)
            line_num = int(index.split('.')[0])
            
            if 1 <= line_num <= len(self.history):
                timestamp, cmd_name, params = self.history[line_num - 1]
                self.execute_command(cmd_name, params)
        except:
            pass