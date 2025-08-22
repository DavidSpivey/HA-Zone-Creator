# App created with a combination of Google Gemini 2.5 Pro, ChatGPT.

# Requirements:
# pip install paho-mqtt requests
#
# Create exe using
# pyinstaller --onefile --noconsole --icon=mmwave.ico --add-data="mmwave.ico;." this.py
import base64
import tkinter as tk
import sys
from tkinter import ttk, messagebox, filedialog
import paho.mqtt.client as mqtt
import threading
import time
import requests
import json
import math
import re
import configparser
import os
import logging
from urllib.parse import urlparse

# --- Debug Logging Setup ---
if getattr(sys, 'frozen', False):
    log_dir = os.path.dirname(sys.executable)
else:
    log_dir = os.path.dirname(os.path.abspath(__file__))

# Ensure the log directory exists
os.makedirs(log_dir, exist_ok=True)
log_file_path = os.path.join(log_dir, 'debug.log')

# Configure logging to write to the file
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler = logging.FileHandler(log_file_path, 'w') # 'w' to overwrite log on each run
log_handler.setFormatter(log_formatter)
logger = logging.getLogger()

# Clear any existing handlers to prevent duplicates, which can happen in some environments
if logger.hasHandlers():
    logger.handlers.clear()

logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)

# Add a handler to also log to the console when running as a script (not compiled)
if not getattr(sys, 'frozen', False):
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

# --- Configuration ---
DEFAULT_MQTT_BROKER = ""
DEFAULT_MQTT_PORT = 1883
DEFAULT_DEVICE_ID = ""

GRID_DIMENSION = 100
X_MIN, X_MAX = -4.0, 4.0
Y_MIN, Y_MAX = 0.0, 8.0
CELL_RESOLUTION = (Y_MAX - Y_MIN) / GRID_DIMENSION

#<a href="https://www.flaticon.com/free-icons/copy" title="copy icons">Copy icons created by Ongicon - Flaticon</a>
copy_b64 = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAlHAAAJRwB2wUbKQAAABx0RVh0U29mdHdhcmUAQWRvYmUgRmlyZXdvcmtzIENTNAay06AAAAIJSURBVDiNhVO/a1NhFD3nvRdL0hQajK2NrQWdnBxaAy5FCVpws1ms9V8Q/AHa/gEuBcVBBxc7CQ7SSRqEbrGN2EFa6mBBWyJBOiWkYprke99xiInvNREP3OXccw733o+PkhCE4zj3JicmF13XpdDqkYTv+9zY2Hgu6XbIIClU8w/nd/Z/7Gv3665tV3GvaDc/bdrMpUx1ID6QDeqddhDJUyTTJ4dHhoeGh5BIJBisWCymCxPp+ML9hTf90f6bbZ/3x3z28V18Pncafd9wIKk1WRvGGKRSKabGRmy1UuXU1NQrktuSttrCzJdlqJaHXjx7ZH0jNQ4bMg0TKkkyDaPCekEAMpJaEwDwa3Xg1yEgASSUy+V08PMAR6Dpq9OOaRoC8DsrdKkAjI6Nol6vgyADNCORCKxsR9szAAKSx5P0fT/IEgBc1w1JewaQQP59XpVKhQQDDSg7k6XjdB7vHysInLs1xx4tNutNGGP+O4GWXi6pXC6TDOVo9sYsPc/rkKEA+ZDjRkEHnLk+A2stjoCDg4Msfi8CgBsKsAIGTgCl1VXl3l2EadTQ/gut9QHPI/siwtr6Wh3AXjDAcR3gWBy8c20FWzsr4N87tRADlt+i+vQ1rgAoSSoFA8q7JZixcbiuB6TPd99FUTBfwL6kj6GdJIEkR5JYPTOOy/ChbjtgfejDNh5YqydB/jcsxQpot2d3xQAAAABJRU5ErkJggg=='

#<a href="https://www.vecteezy.com/free-vector/floppy-disk">Floppy Disk Vectors by Vecteezy</a>
floppy_b64 = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAcIAAAHCABzQ+bngAAABx0RVh0U29mdHdhcmUAQWRvYmUgRmlyZXdvcmtzIENTNAay06AAAAI5SURBVDiNfZK9a9NRFIafc+/9pUlMm6RWHcRqJQUp4mQEJzehS3HzY7O4uouD3cR/QGhVFBfRURHETXAQXEQKXVobP9vGxDat+f59HIc2aWqrZ7rc956H9z3niqqSn/n0oOn7kzmvIncnjjJf+IYRg7WW0dERrLWgiucMlx/P6vuSO/dzKv8WwORnFh4CV1BERKi3GhSWf/CluMTX0gqqSqcEEFQOZFPTZ+4vHgZwwNXOA2cNbb9NcbVMzIvhnCOKoi7AiGBFMCJjGumb/MzCddcVDRTXG6T7j3ByZJh2EJBNpxnsT4CCNVBrh5RrLUwCgBzwagug9Hke30s+t15/5sKpE2gYsSbC84/LAFgjvJxdYbkasn/A60aT09PzWyeBMKBSqdAOQ4xIhw0CkSoxa8lkMmAdbAG6EVAF68gOHeR/pRp1m3cCAFWlHQTorrbtLXhWkJ67LkAV/EgZyTg8I7sgwqZeqAR4Rugk7AKaoXLj7AAXx1KE7A2wKM/mqtx5t0HCyTYgVBiMG8ZzSX5t1CiW1zBGdgCiSDk0lGU8l+TehypVX7HS40AE2oFijSUe70NkJ0BVMcbSDpReySGyPVURfN+nsr6BMeYvBxGpRBwTj/XkElzYaiCxJCKCiNCf2sfxY8N7OuhzlnooiBhElKhVxzVXlx6ZZPpSPJlIlMqWpCdE7F0GqPuKX/9Nq95oRPX1p25u6vxk7uaLyNXd5GJhTeJWiP7xEYxsbqtWrmmzFTxZuD1x7Q91u/L1T1OTtgAAAABJRU5ErkJggg=='

#<a href="https://www.flaticon.com/free-icons/open-folder" title="open folder icons">Open folder icons created by kumakamu - Flaticon</a>
folder_b64 = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAlgAAAJYABbFUIBwAAABx0RVh0U29mdHdhcmUAQWRvYmUgRmlyZXdvcmtzIENTNAay06AAAAG7SURBVDiNxZPNahNhFIaf88100qTGWlCskrgSKW01SAviQgUrCoLeQl0IuvQCvAA3LnTZjTcgQgsSpBQEIVD8wUALQbsQamsTTSXJZCbJZL7joopIdbrownd7OA/ve35EVdmPzL66ATlcmDj+rRbNA9N/VCyfUZ3U6odGEsCtV6Pi7amhyUs5j068E2fACJXtfu7Bsv8IuJUIUDhzbtTj/LHfAICZvMe6H8+6ubERZ1DaAAL0Ynqq+lg/Vd4BuACdWHENtNqWTqSIQF3g7niG6/nUzV9Qx0AtsNx72SwAZ3ego6f0yY0Rvvgxz7ciDg07WAUURMCR3babkcaNwG6urnUWXQTqoWVhK2Lp4QkynmDtvzMLIFnHmXu6nb9zf/2ia1KG15s9pifSZDKGViNOmhkAWVcovm036PqzJu0Jy9WIa1ND2O7eR+UY2KhGlCrhe9VqyQRti+8IF8bShN0E7z+VThlerYbU1rovAFz93ufKzEGGjw4QN/t7AiTrsFQOwA+LAK4IKwcGzfhiqWWCMNmBY4RWaCm+8cuwUQaQI5cLJ7+uBM8I9TR/WdkuxdpG5Kq2PpYA5L9/4w8kwbfirBKxgQAAAABJRU5ErkJggg=='

#<a href="https://www.flaticon.com/free-icons/paper" title="paper icons">Paper icons created by Smashicons - Flaticon</a>
paste_b64 = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAWQAAAFkBqp2phgAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAIiSURBVDiNfZLLaxNRFMZ/d+Y2k2SSiTYxSWmiWC2FFo001Aduqi5UkIIr90L9B0TcunLjxi5dCyqCCBbRhYg7q7hoBPvQPlNrtZKHaWvSNjPXRdqSmGm/1eWec3/nOx9XKKXYVjjc1nPiVPrdPitk/l2vbGRGP39cmpsaUEpV2EUCSHXEIi8t0xfMb2I+HX6lDz9/RiJ5kInFZR7fv7sRCfgK2d+FsdXK+kWl1GY9QCbC+28NnE61rxgW0e5e8sU/BKwQhmnSf+YkI697PJ2GHfN7jOCn6fluIFMP0IRAEwLGsz+Ix+PMfpvEsizKq6sszEwTSXawUFxBE0JsOW6QBCiulemLBnj/6AF1kQDQKnWOHU3ydnTSNQMJkFtZw/J5ORyL7BS+zI9xKP4LXYNKFdJdtpHu1N50JWT566KdUkrldwBBr4HUtQZyMrrM0M16x1IDwjeGvKSK1XEhRK9SalEC/CyUCPl9eKSsC8fVMQG/4tK5WHRuqTrVHTf6pHtbTfmSIrvcGMqVdJnJ2Sy3LzveO0/swT0BuRJMzKum+0gI+ttrFiXAgVAAr6fF1UFmqhnQIuF8e+2sAbS1hjBaGs00P3PXrisoFJ0JwbULWlNNEwKJXQMohfP/5wFwHKVyJSHcMtB1RWJrBfk9V7j3YiTTb5m+4HZD1bbXUx22P1/SzT0zECih3MYDfUfEw7PH9au6RtMOjqPs0XFn4cMM1/8BZ9TFiE+iasAAAAAASUVORK5CYII='

#<a href="https://www.flaticon.com/free-icons/polygon" title="polygon icons">Polygon icons created by Bharat Icons - Flaticon</a>
polygon_b64 = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAB2AAAAdgFOeyYIAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAJRJREFUOI3N0jEOAUEUxvEfUdNoNQpxAfR7mlVoNG6hcQx3kNg4BFolZ0DzijXZhN1mfcmXyfsy83+Tmcc/qQjP0P/1UK8iy5BjEPUdF5xxxRJPbFLALtZ9AhxiGs4w/3aDVA+cwrCuC0h1KxfdBoAPtQ9o8gajuoDyN06wiHybAlboYBwbqwbpENmrqlOBo5qj3L7egUIWKsCtU0QAAAAASUVORK5CYII='

class MMWaveVisualizer:
    def __init__(self, master):
        self.history_stack = []
        self.master = master
        self.master.title("Home Assistant Zone Creator for eMotion Max / Ultra")
        logging.info("Application starting up.")

        # --- Data Storage ---
        self.current_x = 0.0
        self.current_y = 0.0
        self._x_updated = False
        self._y_updated = False
        self.target_square_coords = None
        self.zone_squares = set()
        self.trail_enabled = tk.BooleanVar(value=True)
        self.trail_squares = set()

        # --- Tkinter String Variables ---
        self.device_id = tk.StringVar(value=DEFAULT_DEVICE_ID)
        self.last_known_device_id = "" # To track changes for resubscribing
        self.mqtt_broker = tk.StringVar(value=DEFAULT_MQTT_BROKER)
        self.mqtt_user = tk.StringVar()
        self.mqtt_pass = tk.StringVar()
        self.connection_status = tk.StringVar(value="Status: Disconnected")
        self.ha_address = tk.StringVar()
        self.ha_token = tk.StringVar()
        self.selected_ha_device = tk.StringVar()
        self.ha_status = tk.StringVar(value="HA Status: Idle")

        # --- HA Device Storage ---
        self.ha_devices = {} # Maps friendly name to device ID

        # --- Selection Mode Variables ---
        self.add_mode = tk.BooleanVar(value=True)
        self.add_mode_text = tk.StringVar(value=" + Adding to selection")
        self.diagonal_mode = tk.BooleanVar(value=False)
        self.polygon_selection_active = False
        self.polygon_vertices = []
        self.polygon_lines = []
        self.temp_line = None
        self.last_mouse_pos = None

        # --- UI Elements ---
        self.canvas = None
        self.drag_start_pos = None
        self.drag_shape_id = None
        self.colored_square_ids = {}
        self.save_icon, self.load_icon, self.copy_icon, self.paste_icon, self.polygon_icon = None, None, None, None, None
        self.polygon_button, self.diagonal_button = None, None
        self.ha_device_dropdown = None

        # --- Canvas Sizing ---
        self.canvas_width = 800
        self.canvas_height = 800
        self.cell_pixel_size = self.canvas_width / GRID_DIMENSION

        # --- MQTT Client ---
        self.mqtt_client = None
        self.mqtt_thread = None
        self.original_radar_speed = None

        # --- Correctly determine path for settings file ---
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(base_path, "settings.ini")
        logging.info(f"Settings file path: {self.config_file}")
        logging.info(f"Log file path: {log_file_path}")


        self._load_settings()
        self.last_known_device_id = self.device_id.get()
        self._setup_gui()
        self.master.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Fetch HA devices on startup if configured
        if self.ha_address.get() and self.ha_token.get():
            self._fetch_ha_devices_thread()

    def _setup_gui(self):
        logging.debug("Setting up GUI.")
        try:
            self.save_icon = tk.PhotoImage(data=base64.b64decode(floppy_b64))
            self.load_icon = tk.PhotoImage(data=base64.b64decode(folder_b64))
            self.copy_icon = tk.PhotoImage(data=base64.b64decode(copy_b64))
            self.paste_icon = tk.PhotoImage(data=base64.b64decode(paste_b64))
            self.polygon_icon = tk.PhotoImage(data=base64.b64decode(polygon_b64))
        except Exception as e:
            logging.error(f"Failed to load PhotoImage objects: {e}")
            messagebox.showerror("Icon Error", "Failed to load application icons.")

        main_frame = tk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(main_frame, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5, padx=10)
        self._draw_grid_lines()
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind("<Button-1>", self._on_canvas_press)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)
        self.canvas.bind("<Button-3>", self._on_canvas_press)
        self.canvas.bind("<B3-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-3>", self._on_canvas_release)
        self.canvas.bind("<Motion>", self._on_canvas_move)
        self.canvas.bind("<Double-Button-1>", self._on_polygon_finish)
        self.master.bind("<Control-z>", self._undo_last_action)

        controls_frame = tk.Frame(main_frame, padx=10)
        controls_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # --- MQTT Settings Frame ---
        settings_frame = tk.LabelFrame(controls_frame, text="MQTT Settings", padx=10, pady=10)
        settings_frame.pack(fill=tk.X, pady=5)
        tk.Label(settings_frame, text="Broker:", anchor='w').grid(row=0, column=0, sticky='w', pady=2)
        tk.Entry(settings_frame, textvariable=self.mqtt_broker).grid(row=0, column=1, sticky='ew')
        tk.Label(settings_frame, text="Username:", anchor='w').grid(row=1, column=0, sticky='w', pady=2)
        tk.Entry(settings_frame, textvariable=self.mqtt_user).grid(row=1, column=1, sticky='ew')
        tk.Label(settings_frame, text="Password:", anchor='w').grid(row=2, column=0, sticky='w', pady=2)
        tk.Entry(settings_frame, textvariable=self.mqtt_pass, show="*").grid(row=2, column=1, sticky='ew')
        tk.Label(settings_frame, text="Device ID:", anchor='w').grid(row=3, column=0, sticky='w', pady=2)
        tk.Entry(settings_frame, textvariable=self.device_id).grid(row=3, column=1, sticky='ew')
        settings_frame.grid_columnconfigure(1, weight=1)

        connect_frame = tk.Frame(controls_frame)
        connect_frame.pack(fill=tk.X, pady=5)
        tk.Button(connect_frame, text="Connect", command=self._connect_mqtt).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(connect_frame, text="Disconnect", command=self._disconnect_mqtt).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5,0))
        tk.Label(controls_frame, textvariable=self.connection_status, relief=tk.GROOVE, anchor='w').pack(fill=tk.X, pady=5)

        # --- Zone Actions Frame ---
        zone_frame = tk.LabelFrame(controls_frame, text="Zone Actions", padx=10, pady=10)
        zone_frame.pack(fill=tk.X, pady=10)
        action_buttons_frame = tk.Frame(zone_frame)
        action_buttons_frame.pack(fill=tk.X, pady=(5,10))
        self.polygon_button = tk.Button(action_buttons_frame, image=self.polygon_icon, text=" Polygon", compound="left", command=self._toggle_polygon_mode)
        self.polygon_button.pack(side=tk.LEFT, padx=(0, 5))
        self.diagonal_button = tk.Button(action_buttons_frame, text="Diagonal", command=self._toggle_diagonal_mode)
        self.diagonal_button.pack(side=tk.LEFT)
        self.add_mode_label = tk.Label(zone_frame, textvariable=self.add_mode_text, cursor="hand2")
        self.add_mode_label.bind("<1>", self._toggle_add_mode)
        self.add_mode_label.pack(anchor='w', pady=5)
        tk.Checkbutton(zone_frame, text="Movement trail", variable=self.trail_enabled).pack(anchor='w')
        tk.Frame(zone_frame, height=10).pack()
        tk.Button(zone_frame, image=self.copy_icon, text="  Copy Template", compound="left", command=self._copy_template_to_clipboard).pack(fill=tk.X, pady=(0,2))
        tk.Button(zone_frame, image=self.save_icon, text="  Save Template", compound="left", command=self._save_template_to_file).pack(fill=tk.X, pady=2)
        tk.Button(zone_frame, image=self.paste_icon, text="  Load from Clipboard", compound="left", command=self._load_zone_from_clipboard).pack(fill=tk.X, pady=2)
        tk.Button(zone_frame, image=self.load_icon, text="  Load from File", compound="left", command=self._load_zone_from_file).pack(fill=tk.X, pady=2)
        tk.Button(zone_frame, text="Clear Zones", command=self._clear_zone).pack(fill=tk.X, pady=(10,2))
        tk.Button(zone_frame, text="Clear Movement Trails", command=self._clear_trails).pack(fill=tk.X, pady=2)

        # --- Home Assistant Integration Frame ---
        ha_frame = tk.LabelFrame(controls_frame, text="Home Assistant Connection (Optional)", padx=10, pady=10)
        ha_frame.pack(fill=tk.X, pady=5)
        tk.Label(ha_frame, text="HA Address:", anchor='w').grid(row=0, column=0, sticky='w', pady=2)
        ha_addr_entry = tk.Entry(ha_frame, textvariable=self.ha_address)
        ha_addr_entry.grid(row=0, column=1, sticky='ew')
        ha_addr_entry.bind("<FocusOut>", self._on_ha_address_focus_out)
        tk.Label(ha_frame, text="Access Token:", anchor='w').grid(row=1, column=0, sticky='w', pady=2)
        ha_token_entry = tk.Entry(ha_frame, textvariable=self.ha_token, show="*")
        ha_token_entry.grid(row=1, column=1, sticky='ew')
        ha_token_entry.bind("<FocusOut>", self._fetch_ha_devices_thread)
        tk.Label(ha_frame, text="Device:", anchor='w').grid(row=2, column=0, sticky='w', pady=2)
        self.ha_device_dropdown = ttk.Combobox(ha_frame, textvariable=self.selected_ha_device, state="readonly")
        self.ha_device_dropdown.grid(row=2, column=1, sticky='ew', pady=2)
        self.ha_device_dropdown.bind("<<ComboboxSelected>>", self._on_ha_device_selected)
        tk.Label(ha_frame, textvariable=self.ha_status, font=("Segoe UI", 8)).grid(row=3, column=0, columnspan=2, sticky='ew', pady=(5,0))
        ha_frame.grid_columnconfigure(1, weight=1)

        # --- Traces ---
        self.device_id.trace_add("write", self._validate_and_extract_device_id)
        self.mqtt_broker.trace_add("write", lambda *args: self._save_settings())
        self.mqtt_user.trace_add("write", lambda *args: self._save_settings())
        self.mqtt_pass.trace_add("write", lambda *args: self._save_settings())
        self.ha_address.trace_add("write", lambda *args: self._save_settings())
        self.ha_token.trace_add("write", lambda *args: self._save_settings())

    def _validate_and_extract_device_id(self, *args):
        current_value = self.device_id.get()
        match = re.search(r'([a-fA-F0-9]{32})', current_value)
        if match:
            extracted_id = match.group(1).lower()
            if extracted_id != self.last_known_device_id:
                logging.info(f"Device ID changed from '{self.last_known_device_id}' to '{extracted_id}'.")
                if self.mqtt_client and self.mqtt_client.is_connected():
                    self._restore_radar_speed(self.last_known_device_id)
                    old_topics = [f"home/{self.last_known_device_id}_tar_1_{ax}/status" for ax in "xy"]
                    old_topics.append(f"home/config/{self.last_known_device_id}_config_radar_i/status")
                    self.mqtt_client.unsubscribe(old_topics)
                    logging.info(f"Unsubscribed from old device topics.")
                    self._subscribe_to_topics(self.mqtt_client, extracted_id)
                    self._clear_zone()
                    self._clear_trails()
                self.last_known_device_id = extracted_id
            if extracted_id != current_value:
                self.device_id.trace_remove("write", self.device_id.trace_info()[0][1])
                self.device_id.set(extracted_id)
                self.device_id.trace_add("write", self._validate_and_extract_device_id)
            self._save_settings()

    def _toggle_diagonal_mode(self):
        self.diagonal_mode.set(not self.diagonal_mode.get())
        self.diagonal_button.config(relief=tk.SUNKEN if self.diagonal_mode.get() else tk.RAISED)

    def _toggle_add_mode(self, event=None):
        self.add_mode.set(not self.add_mode.get())
        self.add_mode_text.set(" + Adding to selection" if self.add_mode.get() else " - Removing from selection")

    def _undo_last_action(self, event=None):
        if self.polygon_selection_active and self.polygon_vertices:
            self._undo_polygon_point()
            return
        if not self.history_stack:
            logging.info("Nothing to undo")
            return
        self.zone_squares = self.history_stack.pop()
        self._redraw_canvas()
        logging.info("Undo completed.")

    def _load_settings(self):
        logging.info(f"Attempting to load settings from {self.config_file}")
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            config.read(self.config_file)
            if "MQTT" in config:
                self.mqtt_broker.set(config["MQTT"].get("broker", DEFAULT_MQTT_BROKER))
                self.device_id.set(config["MQTT"].get("device_id", DEFAULT_DEVICE_ID))
                self.mqtt_user.set(config["MQTT"].get("username", ""))
                self.mqtt_pass.set(config["MQTT"].get("password", ""))
            if "HOME_ASSISTANT" in config:
                self.ha_address.set(config["HOME_ASSISTANT"].get("address", ""))
                self.ha_token.set(config["HOME_ASSISTANT"].get("token", ""))
            logging.info("Settings loaded successfully.")
        else:
            logging.warning("Settings file not found. Using defaults.")

    def _save_settings(self):
        config = configparser.ConfigParser()
        config["MQTT"] = {
            "broker": self.mqtt_broker.get(),
            "device_id": self.device_id.get(),
            "username": self.mqtt_user.get(),
            "password": self.mqtt_pass.get()
        }
        config["HOME_ASSISTANT"] = {
            "address": self.ha_address.get(),
            "token": self.ha_token.get()
        }
        try:
            with open(self.config_file, "w") as f:
                config.write(f)
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")

    def _on_canvas_resize(self, event):
        size = min(event.width, event.height)
        self.cell_pixel_size = size / GRID_DIMENSION
        self.canvas_width = size
        self.canvas_height = size
        self._redraw_canvas()

    def _draw_grid_lines(self):
        for i in range(1, GRID_DIMENSION):
            pos_y = i * self.cell_pixel_size
            self.canvas.create_line(0, pos_y, self.canvas_width, pos_y, fill="lightblue")
            pos_x = i * self.cell_pixel_size
            self.canvas.create_line(pos_x, 0, pos_x, self.canvas_height, fill="lightblue")

    def _redraw_canvas(self):
        self.canvas.delete("all")
        self.colored_square_ids.clear()
        self._draw_grid_lines()
        all_squares = self.zone_squares.union(self.trail_squares)
        if self.target_square_coords:
            all_squares.add(self.target_square_coords)
        for r, c in all_squares:
            self._update_square_color(r, c)
        self._redraw_polygon_lines()

    def _redraw_polygon_lines(self):
        if not self.polygon_selection_active: return
        self.polygon_lines.clear()
        if len(self.polygon_vertices) > 1:
            for i in range(len(self.polygon_vertices) - 1):
                line_id = self.canvas.create_line(self.polygon_vertices[i], self.polygon_vertices[i+1], fill="green", width=2)
                self.polygon_lines.append(line_id)
        if self.polygon_vertices and self.last_mouse_pos:
            if self.temp_line: self.canvas.delete(self.temp_line)
            last_point = self.polygon_vertices[-1]
            self.temp_line = self.canvas.create_line(last_point, self.last_mouse_pos, fill="green", width=2, dash=(4, 4))

    def _update_square_color(self, r, c):
        if not (0 <= r < GRID_DIMENSION and 0 <= c < GRID_DIMENSION): return
        is_target = (r, c) == self.target_square_coords
        is_zone = (r, c) in self.zone_squares
        is_trail = (r, c) in self.trail_squares
        item_id = self.colored_square_ids.get((r, c))
        if not is_target and not is_zone and not is_trail:
            if item_id: self.canvas.delete(item_id); del self.colored_square_ids[(r, c)]
            return
        color = "blue" if is_target else "red" if is_trail else "orange"
        if item_id:
            self.canvas.itemconfig(item_id, fill=color)
        else:
            x1, y1 = c * self.cell_pixel_size, r * self.cell_pixel_size
            x2, y2 = x1 + self.cell_pixel_size, y1 + self.cell_pixel_size
            new_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
            self.colored_square_ids[(r, c)] = new_id
        if is_target or is_trail:
            self.canvas.tag_raise(self.colored_square_ids.get((r, c)))

    # --- Home Assistant Methods ---
    def _on_ha_address_focus_out(self, event=None):
        addr = self.ha_address.get().strip()
        if not addr: return
        parsed = urlparse(addr)
        if not parsed.scheme:
            addr = "http://" + addr
            parsed = urlparse(addr)
        if not parsed.port:
            addr = f"{parsed.scheme}://{parsed.hostname}:8123"
        self.ha_address.set(addr)
        self._fetch_ha_devices_thread()

    def _fetch_ha_devices_thread(self, event=None):
        if self.ha_address.get() and self.ha_token.get():
            thread = threading.Thread(target=self._fetch_ha_devices, daemon=True)
            thread.start()

    def _fetch_ha_devices_thread(self, event=None):
        if self.ha_address.get() and self.ha_token.get():
            thread = threading.Thread(target=self.fetch_ha_devices, daemon=True)
            thread.start()

    def fetch_ha_devices(self):
        """Pull mmWave devices from Home Assistant via states + template for names."""
        self.master.after(0, self.ha_status.set, "HA Status: Fetching devices…")

        address = self.ha_address.get().strip().rstrip('/')
        token   = self.ha_token.get().strip()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Step 1: Get entity states
        try:
            states_resp = requests.get(f"{address}/api/states", headers=headers, timeout=15)
            states_resp.raise_for_status()
            entities = states_resp.json()
        except Exception as exc:
            logging.error("Failed to fetch states: %s", exc)
            self.master.after(0, self.ha_status.set, f"HA Status: error – {exc}")
            return

        # Step 2: Collect unique device ids
        device_ids = set()
        entity_lookup = {}
        for ent in entities:
            ent_id = ent.get("entity_id")
            if not ent_id:
                continue

            if ent_id.startswith("sensor.lnlinkha_") or ent_id.startswith("binary_sensor.lnlinkha_"):
                match = re.match(r"^[a-z_]+\.lnlinkha_([a-fA-F0-9]{32})_", ent_id)
                if match:
                    dev_id = match.group(1).lower()
                    device_ids.add(dev_id)
                    entity_lookup[dev_id] = ent_id  # keep one representative entity

        device_map = {}

        # Step 3: For each device id, resolve the actual device name via /api/template
        for dev_id in device_ids:
            rep_entity = entity_lookup[dev_id]
            jinja_template = (
                "{{ device_attr('" + rep_entity + "', 'name_by_user') "
                "or device_attr('" + rep_entity + "', 'name') }}"
            )
            payload = {"template": jinja_template}
            try:
                tmpl_resp = requests.post(f"{address}/api/template", headers=headers, json=payload, timeout=10)
                tmpl_resp.raise_for_status()
                name = tmpl_resp.text.strip().strip('"')
            except Exception as exc:
                logging.warning("Template lookup failed for %s: %s", rep_entity, exc)
                name = f"mmWave {dev_id[:6]}"

            if not name:
                name = f"mmWave {dev_id[:6]}"

            device_map[dev_id] = name

        # Step 4: Update UI
        self.ha_devices.clear()
        names_for_dropdown = []
        for dev_id, friendly in device_map.items():
            self.ha_devices[friendly] = dev_id
            names_for_dropdown.append(friendly)

        self.master.after(
            0,
            self._update_ha_device_dropdown,
            sorted(names_for_dropdown)
        )
        self.master.after(0, self.ha_status.set,
                          f"HA Status: {len(names_for_dropdown)} device(s) loaded")

    def _update_ha_device_dropdown(self, device_names):
        self.ha_device_dropdown['values'] = device_names
        if device_names:
            self.ha_status.set(f"HA Status: Found {len(device_names)} device(s).")
            # Set to the first device if nothing is selected or current selection is invalid
            if not self.selected_ha_device.get() in device_names:
                self.selected_ha_device.set(device_names[0])
            self._on_ha_device_selected()
        else:
            self.ha_status.set("HA Status: No compatible devices found.")
            self.selected_ha_device.set("")

    def _on_ha_device_selected(self, event=None):
        selected_name = self.selected_ha_device.get()
        if selected_name in self.ha_devices:
            new_device_id = self.ha_devices[selected_name]
            if new_device_id != self.device_id.get():
                logging.info(f"Selected HA device '{selected_name}' with ID '{new_device_id}'")
                self.device_id.set(new_device_id)
                # The trace on device_id will handle clearing and reconnecting
                if not (self.mqtt_client and self.mqtt_client.is_connected()):
                    self._connect_mqtt()

    # --- MQTT Methods ---
    def _connect_mqtt(self):
        self._disconnect_mqtt(); time.sleep(0.1)
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self._on_mqtt_connect
        self.mqtt_client.on_message = self._on_mqtt_message
        self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
        user, pswd = self.mqtt_user.get(), self.mqtt_pass.get()
        if user: self.mqtt_client.username_pw_set(user, pswd)
        broker = self.mqtt_broker.get()
        if not broker: messagebox.showerror("Error", "MQTT Broker address cannot be empty."); return
        self.connection_status.set(f"Status: Connecting to {broker}...")
        try:
            self.mqtt_client.connect(broker, DEFAULT_MQTT_PORT, 60)
            self.mqtt_thread = threading.Thread(target=self.mqtt_client.loop_forever, daemon=True)
            self.mqtt_thread.start()
        except Exception as e:
            messagebox.showerror("MQTT Error", f"Could not connect to broker: {e}")
            self.connection_status.set("Status: Connection failed")

    def _disconnect_mqtt(self):
        if self.mqtt_client and self.mqtt_client.is_connected():
            self._restore_radar_speed(self.last_known_device_id)
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            logging.info("MQTT Disconnected.")
        if self.target_square_coords:
            self.target_square_coords = None
            self._redraw_canvas()

    def _subscribe_to_topics(self, client, device_id=None):
        dev_id = device_id or self.device_id.get()
        if not dev_id:
            logging.warning("Cannot subscribe, Device ID is empty.")
            return
        topics = [(f"home/{dev_id}_tar_1_{ax}/status", 0) for ax in "xy"]
        topics.append((f"home/config/{dev_id}_config_radar_i/status", 0))
        client.subscribe(topics)
        logging.info(f"Subscribed to topics for device {dev_id}")

    def _on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info("MQTT Connected Successfully."); self.connection_status.set("Status: Connected")
            self._subscribe_to_topics(client)
        else:
            errors = {1:"protocol version", 2:"client identifier", 3:"server unavailable", 4:"bad username/password", 5:"not authorised"}
            err_txt = f"Failed to connect: {errors.get(rc, 'Unknown error')} (Code: {rc})"
            logging.error(err_txt)
            messagebox.showerror("MQTT Error", err_txt); self.connection_status.set(f"Status: Failed")

    def _on_mqtt_disconnect(self, client, userdata, rc):
        self.connection_status.set("Status: Disconnected"); logging.info(f"MQTT client disconnected with code: {rc}")
        if self.target_square_coords: self.target_square_coords = None; self._redraw_canvas()

    def _on_mqtt_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode()
            dev_id = self.device_id.get()
            if msg.topic == f"home/config/{dev_id}_config_radar_i/status":
                if self.original_radar_speed is None:
                    self.original_radar_speed = payload
                    logging.info(f"Original radar speed captured: {payload}")
                    client.publish(f"home/config/{dev_id}_config_radar_i/set", "0.5")
            elif "_tar_1_x" in msg.topic: self.current_x = float(payload); self._x_updated = True
            elif "_tar_1_y" in msg.topic: self.current_y = float(payload); self._y_updated = True
            if self._x_updated and self._y_updated:
                self._x_updated = self._y_updated = False
                self.master.after(0, self._update_target_on_grid)
        except (ValueError, UnicodeDecodeError) as e:
            logging.error(f"MQTT message parse error: {e}")

    def _restore_radar_speed(self, device_id):
        if self.mqtt_client and self.mqtt_client.is_connected() and self.original_radar_speed is not None:
            topic = f"home/config/{device_id}_config_radar_i/set"
            self.mqtt_client.publish(topic, self.original_radar_speed)
            logging.info(f"Restored radar speed '{self.original_radar_speed}' to {topic}")
        self.original_radar_speed = None

    def _update_target_on_grid(self):
        if self.current_x == 0.0 and self.current_y == 0.0:
            self.target_square_coords = None
        else:
            col = int(((X_MAX - self.current_x) / (X_MAX - X_MIN)) * GRID_DIMENSION)
            row = int(((self.current_y - Y_MIN) / (Y_MAX - Y_MIN)) * GRID_DIMENSION)
            self.target_square_coords = (max(0, min(GRID_DIMENSION - 1, row)), max(0, min(GRID_DIMENSION - 1, col)))
            if self.trail_enabled.get(): self.trail_squares.add(self.target_square_coords)
        self._redraw_canvas()

    def _get_coords_from_event(self, event):
        c = int(event.x / self.cell_pixel_size); r = int(event.y / self.cell_pixel_size); return r, c

    def _on_canvas_press(self, event):
        if self.polygon_selection_active: self._add_polygon_point(event); return
        self.drag_start_pos = (event.x, event.y)

    def _on_canvas_drag(self, event):
        if self.polygon_selection_active or not self.drag_start_pos: return
        if self.drag_shape_id: self.canvas.delete(self.drag_shape_id)
        x1, y1 = self.drag_start_pos; x2, y2 = event.x, event.y
        vertices = self._get_rotated_rect_vertices(x1, y1, x2, y2) if self.diagonal_mode.get() else [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
        self.drag_shape_id = self.canvas.create_polygon(vertices, outline="red", fill="", width=2)

    def _on_canvas_release(self, event):
        if self.polygon_selection_active or not self.drag_start_pos: return
        if self.drag_shape_id: self.canvas.delete(self.drag_shape_id); self.drag_shape_id = None
        x1, y1 = self.drag_start_pos; x2, y2 = event.x, event.y
        is_click = abs(x1 - x2) < 4 and abs(y1 - y2) < 4
        vertices = self._get_rotated_rect_vertices(x1, y1, x2, y2) if self.diagonal_mode.get() and not is_click else [(min(x1, x2), min(y1, y2)),(max(x1, x2), min(y1, y2)),(max(x1, x2), max(y1, y2)),(min(x1, x2), max(y1, y2))]
        min_x, max_x = min(v[0] for v in vertices), max(v[0] for v in vertices)
        min_y, max_y = min(v[1] for v in vertices), max(v[1] for v in vertices)
        start_r, start_c = self._get_coords_from_event(type('',(),{'x':min_x,'y':min_y})())
        end_r, end_c = self._get_coords_from_event(type('',(),{'x':max_x,'y':max_y})())
        use_add = not self.add_mode.get() if event.num == 3 else self.add_mode.get()
        self.history_stack.append(self.zone_squares.copy())
        for r in range(start_r, end_r + 1):
            for c in range(start_c, end_c + 1):
                if not (0 <= r < GRID_DIMENSION and 0 <= c < GRID_DIMENSION): continue
                center = ((c + 0.5) * self.cell_pixel_size, (r + 0.5) * self.cell_pixel_size)
                if self._is_point_in_polygon(center, vertices):
                    if use_add: self.zone_squares.add((r, c))
                    else: self.zone_squares.discard((r, c))
        self._redraw_canvas()
        self.drag_start_pos = None

    def _get_rotated_rect_vertices(self, x_a, y_a, x_c, y_c):
        s_c = ((x_c - x_a) + (y_c - y_a)) / 2; t_c = ((x_c - x_a) - (y_c - y_a)) / 2
        return [(x_a, y_a), (x_a + t_c, y_a - t_c), (x_c, y_c), (x_a + s_c, y_a + s_c)]

    def _is_point_in_polygon(self, point, polygon):
        x, y = point; n = len(polygon); inside = False
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y) and y <= max(p1y, p2y) and x <= max(p1x, p2x):
                if p1y != p2y: xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                if p1x == p2x or x <= xinters: inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def _clear_zone(self): self.zone_squares.clear(); self._redraw_canvas(); logging.info("Zone cleared.")
    def _clear_trails(self): self.trail_squares.clear(); self._redraw_canvas(); logging.info("Trails cleared.")
    def _copy_template_to_clipboard(self):
        if not self.zone_squares: messagebox.showwarning("Empty Zone", "No zone selected."); return
        template = self._generate_jinja_template()
        self.master.clipboard_clear(); self.master.clipboard_append(template)
        messagebox.showinfo("Success", "Template copied to clipboard!")

    def _save_template_to_file(self):
        if not self.zone_squares: messagebox.showwarning("Empty Zone", "No zone selected."); return
        fpath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if not fpath: return
        template = self._generate_jinja_template()
        try:
            with open(fpath, 'w') as f: f.write(template)
            messagebox.showinfo("Success", f"Template saved to {fpath}")
        except Exception as e: messagebox.showerror("Error", f"Failed to save file: {e}")

    def _load_zone_from_clipboard(self):
        try: self._parse_and_load_zone(self.master.clipboard_get())
        except tk.TclError: messagebox.showwarning("Clipboard Empty", "Clipboard is empty.")
        except Exception as e: messagebox.showerror("Parsing Error", f"Could not parse template: {e}")

    def _load_zone_from_file(self):
        fpath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not fpath: return
        try:
            with open(fpath, 'r') as f: self._parse_and_load_zone(f.read())
        except Exception as e: messagebox.showerror("Error", f"Failed to load or parse file: {e}")

    def _toggle_polygon_mode(self):
        self.polygon_selection_active = not self.polygon_selection_active
        self.polygon_button.config(relief=tk.SUNKEN if self.polygon_selection_active else tk.RAISED)
        if self.polygon_selection_active:
            self.diagonal_mode.set(False); self.diagonal_button.config(relief=tk.RAISED)
        else: self._cancel_polygon_drawing()

    def _cancel_polygon_drawing(self):
        self._clear_current_polygon()
        if self.polygon_selection_active:
            self.polygon_selection_active = False; self.polygon_button.config(relief=tk.RAISED)

    def _clear_current_polygon(self):
        if self.temp_line: self.canvas.delete(self.temp_line); self.temp_line = None
        for line in self.polygon_lines: self.canvas.delete(line)
        self.polygon_lines.clear(); self.polygon_vertices.clear()

    def _add_polygon_point(self, event):
        point = (event.x, event.y)
        if self.polygon_vertices:
            self.polygon_lines.append(self.canvas.create_line(self.polygon_vertices[-1], point, fill="green", width=2))
        self.polygon_vertices.append(point)

    def _on_canvas_move(self, event):
        self.last_mouse_pos = (event.x, event.y)
        if not self.polygon_selection_active or not self.polygon_vertices: return
        if self.temp_line: self.canvas.delete(self.temp_line)
        self.temp_line = self.canvas.create_line(self.polygon_vertices[-1], self.last_mouse_pos, fill="green", width=2, dash=(4, 4))

    def _on_polygon_finish(self, event):
        if not self.polygon_selection_active or len(self.polygon_vertices) < 3:
            if self.polygon_selection_active and self.polygon_vertices: messagebox.showwarning("Polygon Error", "Polygon needs at least 3 points.")
            self._cancel_polygon_drawing(); return
        self.history_stack.append(self.zone_squares.copy())
        vertices = self.polygon_vertices
        min_x, max_x = min(v[0] for v in vertices), max(v[0] for v in vertices)
        min_y, max_y = min(v[1] for v in vertices), max(v[1] for v in vertices)
        start_r, start_c = self._get_coords_from_event(type('',(),{'x':min_x,'y':min_y})())
        end_r, end_c = self._get_coords_from_event(type('',(),{'x':max_x,'y':max_y})())
        use_add = self.add_mode.get()
        for r in range(start_r, end_r + 1):
            for c in range(start_c, end_c + 1):
                if not (0 <= r < GRID_DIMENSION and 0 <= c < GRID_DIMENSION): continue
                center = ((c + 0.5) * self.cell_pixel_size, (r + 0.5) * self.cell_pixel_size)
                if self._is_point_in_polygon(center, vertices):
                    if use_add: self.zone_squares.add((r, c))
                    else: self.zone_squares.discard((r, c))
        self._redraw_canvas()
        self._clear_current_polygon()
        logging.info("Polygon selection applied.")

    def _undo_polygon_point(self):
        if not self.polygon_vertices: return
        self.polygon_vertices.pop()
        if self.polygon_lines: self.canvas.delete(self.polygon_lines.pop())
        if not self.polygon_vertices and self.temp_line: self.canvas.delete(self.temp_line); self.temp_line = None

    def _parse_and_load_zone(self, template):
        new_zone = set()
        match = re.search(r"\{\{\s*(.*?)\s*\}\}", template, re.DOTALL)
        if not match: raise ValueError("Could not find main condition block {{ ... }}")
        cond_str = " ".join(match.group(1).split())
        row_conds = []; level = 0; last_split = 0
        for i, char in enumerate(cond_str):
            if char == '(': level += 1
            elif char == ')': level -= 1
            if level == 0 and cond_str[i:i+4] == ' or ':
                row_conds.append(cond_str[last_split:i]); last_split = i + 4
        row_conds.append(cond_str[last_split:])
        y_pat = re.compile(r"y >= ([\d\.-]+)"); x_pat = re.compile(r"x >= ([\d\.-]+) and x < ([\d\.-]+)")
        for row_str in row_conds:
            y_match = y_pat.search(row_str)
            if not y_match: continue
            r = round(float(y_match.group(1)) / CELL_RESOLUTION)
            for x_match in x_pat.finditer(row_str):
                x_low, x_high = map(float, x_match.groups())
                c_start = round(((X_MAX - x_high) / (X_MAX - X_MIN)) * GRID_DIMENSION)
                c_end = round(((X_MAX - x_low) / (X_MAX - X_MIN)) * GRID_DIMENSION)
                for c in range(c_start, c_end):
                    if 0 <= r < GRID_DIMENSION and 0 <= c < GRID_DIMENSION: new_zone.add((r, c))
        if not new_zone: raise ValueError("No valid zone conditions found")
        self.zone_squares = new_zone; self._redraw_canvas()
        messagebox.showinfo("Success", f"Loaded {len(new_zone)} squares.")

    def _generate_jinja_template(self):
        if not self.zone_squares: return ""
        rows = {}
        for r, c in self.zone_squares: rows.setdefault(r, []).append(c)
        row_conds = []
        for r, cols in sorted(rows.items()):
            cols.sort()
            y_low, y_high = r * CELL_RESOLUTION, (r + 1) * CELL_RESOLUTION
            segments = []; start = cols[0]
            for i in range(1, len(cols)):
                if cols[i] != cols[i-1] + 1: segments.append((start, cols[i-1])); start = cols[i]
            segments.append((start, cols[-1]))
            x_conds = []
            for c_min, c_max in segments:
                x_high = X_MAX - (c_min * CELL_RESOLUTION)
                x_low = X_MAX - ((c_max + 1) * CELL_RESOLUTION)
                x_conds.append(f"(x >= {x_low:.2f} and x < {x_high:.2f})")
            row_conds.append(f"((y >= {y_low:.2f} and y < {y_high:.2f}) and ({' or '.join(x_conds)}))")
        full_cond = " or ".join(row_conds)
        return f"{{% set x = states('{self.get_sensor_entity_id('x')}') | float(0) %}}\n{{% set y = states('{self.get_sensor_entity_id('y')}') | float(0) %}}\n{{{{ {full_cond} }}}}"

    def get_sensor_entity_id(self, axis):
        axis_map = {'x': 7, 'y': 8}
        return f"sensor.lnlinkha_{self.device_id.get()}_{axis_map[axis]}"

    def _on_closing(self):
        self._restore_radar_speed(self.last_known_device_id)
        self._save_settings()
        logging.info("Closing application...")
        self._disconnect_mqtt()
        self.master.destroy()

# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    try:
        logging.info("Main execution block started.")
        app = MMWaveVisualizer(root)
        logging.info("Application instance created. Starting mainloop.")
        root.mainloop()
    except Exception as e:
        logging.critical(f"A fatal error occurred: {e}", exc_info=True)
        messagebox.showerror("Fatal Error", f"An unexpected error occurred:\n\n{e}\n\nSee debug.log for details.")
        if 'root' in locals() and root.winfo_exists():
            root.destro
