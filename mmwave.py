# App created with a combination of Google Gemini 2.5 Pro, ChatGPT.

# Requirements:
# pip install paho-mqtt
#
# Create exe using
# pyinstaller --onefile --noconsole --icon=mmwave.ico --add-data="mmwave.ico;." this.py
import base64
import tkinter as tk
import sys
from tkinter import messagebox, filedialog
import paho.mqtt.client as mqtt
import threading
import time
import collections
import math
import re
import configparser
import os

# --- Configuration ---
DEFAULT_MQTT_BROKER = ""
DEFAULT_MQTT_PORT = 1883
DEFAULT_DEVICE_ID = "e04b410156ad000000000000d6ac0000"

GRID_DIMENSION = 100
X_MIN, X_MAX = -4.0, 4.0
Y_MIN, Y_MAX = 0.0, 8.0
CELL_RESOLUTION = (Y_MAX - Y_MIN) / GRID_DIMENSION

# Windows App Icon <a href="https://www.flaticon.com/free-icons/sine-wave-graphic" title="sine wave graphic icons">Sine wave graphic icons created by Three musketeers - Flaticon</a>

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
        self.master.title("mmWave Sensor Zone Creator for Home Assistant")

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
        self.mqtt_broker = tk.StringVar(value=DEFAULT_MQTT_BROKER)
        self.mqtt_user = tk.StringVar()
        self.mqtt_pass = tk.StringVar()
        self.connection_status = tk.StringVar(value="Status: Disconnected")

        # --- Selection Mode Variables ---
        self.add_mode = tk.BooleanVar(value=True)
        self.add_mode_text = tk.StringVar(value=" + Adding to selection")
        self.diagonal_mode = tk.BooleanVar(value=False)
        self.polygon_selection_active = False
        self.polygon_vertices = []
        self.polygon_lines = []
        self.temp_line = None


        # --- UI Elements ---
        self.canvas = None
        self.drag_start_pos = None
        self.drag_shape_id = None
        self.colored_square_ids = {} # (r, c) -> item_id for performance
        self.save_icon = tk.PhotoImage(data=base64.b64decode(floppy_b64))
        self.load_icon = tk.PhotoImage(data=base64.b64decode(folder_b64))
        self.copy_icon = tk.PhotoImage(data=base64.b64decode(copy_b64))
        self.paste_icon = tk.PhotoImage(data=base64.b64decode(paste_b64))
        self.polygon_icon = tk.PhotoImage(data=base64.b64decode(polygon_b64))
        self.polygon_button = None

        # --- Canvas Sizing ---
        self.canvas_width = 800
        self.canvas_height = 800
        self.cell_pixel_size = self.canvas_width / GRID_DIMENSION

        # --- MQTT Client ---
        self.mqtt_client = None
        self.mqtt_thread = None
        self.last_known_device_id = None # For dynamic topic changes
        self._device_id_trace_active = True # Flag to prevent recursion in trace

        # --- Correctly determine path for settings file ---
        if getattr(sys, 'frozen', False):
            # Running as a compiled executable (PyInstaller)
            base_path = os.path.dirname(sys.executable)
        else:
            # Running from the Python interpreter
            base_path = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(base_path, "settings.ini")

        self._load_settings()
        self._setup_gui()
        self.master.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_gui(self):
        main_frame = tk.Frame(self.master)
        top_window = main_frame.winfo_toplevel()
        # --- CORRECTED ICON LOADING ---
        # Check compiled status, change window icon conditionally
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # Running as a compiled executable
            # Build the path to the icon file in the temporary directory
            icon_path = os.path.join(sys._MEIPASS, 'mmwave.ico')
            top_window.iconbitmap(icon_path)
        else:
            # Running from the Python interpreter (uncompiled)
            # Ensure the icon file exists in the same directory as the script
            icon_path = os.path.join(os.path.dirname(__file__), 'mmwave.ico')
            if os.path.exists(icon_path):
                top_window.iconbitmap(icon_path)
            else:
                print("Icon file 'mmwave.ico' not found. Skipping icon setting.")

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

        settings_frame = tk.LabelFrame(controls_frame, text="MQTT Settings", padx=10, pady=10)
        settings_frame.pack(fill=tk.X, pady=5)
        tk.Label(settings_frame, text="Broker:", anchor='w').grid(row=0, column=0, sticky='w', pady=2)
        tk.Entry(settings_frame, textvariable=self.mqtt_broker).grid(row=0, column=1, sticky='ew')
        self.mqtt_broker.trace_add("write", lambda *args: self._save_settings())
        tk.Label(settings_frame, text="Username:", anchor='w').grid(row=1, column=0, sticky='w', pady=2)
        tk.Entry(settings_frame, textvariable=self.mqtt_user).grid(row=1, column=1, sticky='ew')
        self.mqtt_user.trace_add("write", lambda *args: self._save_settings())
        tk.Label(settings_frame, text="Password:", anchor='w').grid(row=2, column=0, sticky='w', pady=2)
        tk.Entry(settings_frame, textvariable=self.mqtt_pass, show="*").grid(row=2, column=1, sticky='ew')
        self.mqtt_pass.trace_add("write", lambda *args: self._save_settings())
        tk.Label(settings_frame, text="Device ID:", anchor='w').grid(row=3, column=0, sticky='w', pady=2)
        tk.Entry(settings_frame, textvariable=self.device_id).grid(row=3, column=1, sticky='ew')
        # Combined trace for saving and handling device ID changes
        self.device_id.trace_add("write", self._handle_device_id_change)
        self.last_known_device_id = self.device_id.get() # Initialize last known ID

        settings_frame.grid_columnconfigure(1, weight=1)

        connect_frame = tk.Frame(controls_frame)
        connect_frame.pack(fill=tk.X, pady=5)
        tk.Button(connect_frame, text="Connect", command=self._connect_mqtt).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(connect_frame, text="Disconnect", command=self._disconnect_mqtt).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5,0))

        tk.Label(controls_frame, textvariable=self.connection_status, relief=tk.GROOVE, anchor='w').pack(fill=tk.X, pady=5)

        zone_frame = tk.LabelFrame(controls_frame, text="Zone Actions", padx=10, pady=10)
        zone_frame.pack(fill=tk.X, pady=10)

        action_buttons_frame = tk.Frame(zone_frame)
        action_buttons_frame.pack(fill=tk.X, pady=(5,10))
        self.polygon_button = tk.Button(action_buttons_frame, image=self.polygon_icon, text="  Polygon Selection", compound="left", command=self._toggle_polygon_mode)
        self.polygon_button.pack(side=tk.LEFT, padx=(0, 5))
        self.diagonal_button = tk.Button(zone_frame, text="Select Diagonally", command=self._toggle_diagonal_mode)
        self.diagonal_button.pack(anchor='w')

        self.add_mode_label = tk.Label(zone_frame, textvariable=self.add_mode_text, cursor="hand2")
        self.add_mode_label.bind("<1>", self._toggle_add_mode)
        self.add_mode_label.pack(anchor='w', pady=5)
        # Removed command from checkbutton to prevent trail clearing on uncheck
        tk.Checkbutton(zone_frame, text="Movement trail", variable=self.trail_enabled).pack(anchor='w')

        tk.Frame(zone_frame, height=10).pack()

        tk.Button(zone_frame, image=self.copy_icon, text="  Copy Template", compound="left", command=self._copy_template_to_clipboard).pack(fill=tk.X, pady=(0,2))
        tk.Button(zone_frame, image=self.save_icon, text="  Save Template to File", compound="left", command=self._save_template_to_file).pack(fill=tk.X, pady=2)
        tk.Button(zone_frame, image=self.paste_icon, text="  Load from Clipboard", compound="left", command=self._load_zone_from_clipboard).pack(fill=tk.X, pady=2)
        tk.Button(zone_frame, image=self.load_icon, text="  Load from File", compound="left", command=self._load_zone_from_file).pack(fill=tk.X, pady=2)
        tk.Button(zone_frame, text="Clear Zones", command=self._clear_zone).pack(fill=tk.X, pady=(10,2))
        # Added new button to clear movement trails
        tk.Button(zone_frame, text="Clear Movement Trails", command=self._clear_trail).pack(fill=tk.X, pady=2)

    def _toggle_diagonal_mode(self):
        self.diagonal_mode.set(not self.diagonal_mode.get())
        if self.diagonal_mode.get():
            self.diagonal_button.config(relief=tk.SUNKEN)
        else:
            self.diagonal_button.config(relief=tk.RAISED)

    def _toggle_add_mode(self, event=None):
        self.add_mode.set(not self.add_mode.get())
        self.add_mode_text.set(" + Adding to selection" if self.add_mode.get() else " - Removing from selection")

    def _undo_last_action(self, event=None):
        if self.polygon_selection_active and self.polygon_vertices:
            self._undo_polygon_point()
            return
        if not self.history_stack:
            print("Nothing to undo")
            return
        self.zone_squares = self.history_stack.pop()
        self._redraw_canvas()
        print("Undo completed.")

    def _load_settings(self):
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            config.read(self.config_file)
            if "MQTT" in config:
                self.mqtt_broker.set(config["MQTT"].get("broker", DEFAULT_MQTT_BROKER))
                self.device_id.set(config["MQTT"].get("device_id", DEFAULT_DEVICE_ID))
                self.mqtt_user.set(config["MQTT"].get("username", ""))
                self.mqtt_pass.set(config["MQTT"].get("password", ""))

    def _save_settings(self):
        config = configparser.ConfigParser()
        config["MQTT"] = {
            "broker": self.mqtt_broker.get(),
            "device_id": self.device_id.get(),
            "username": self.mqtt_user.get(),
            "password": self.mqtt_pass.get()
        }
        with open(self.config_file, "w") as f:
            config.write(f)

    def _handle_device_id_change(self, *args):
        """Extracts Device ID, saves settings, and handles MQTT topic changes."""
        if not self._device_id_trace_active:
            return

        current_value = self.device_id.get()
        match = re.search(r'([a-fA-F0-9]{32})', current_value)

        extracted_id = match.group(1) if match else current_value

        # Update the entry box if the extracted ID is different
        if extracted_id != current_value:
            self._device_id_trace_active = False # Prevent recursion
            self.device_id.set(extracted_id)
            self._device_id_trace_active = True

        # Save settings regardless of change
        self._save_settings()

        # Handle topic change if the valid ID has changed
        if extracted_id and extracted_id != self.last_known_device_id:
            print(f"Device ID changed from {self.last_known_device_id} to {extracted_id}")

            # If connected, unsubscribe from old topics
            if self.mqtt_client and self.mqtt_client.is_connected() and self.last_known_device_id:
                old_topic_x = f"home/{self.last_known_device_id}_tar_1_x/status"
                old_topic_y = f"home/{self.last_known_device_id}_tar_1_y/status"
                self.mqtt_client.unsubscribe([old_topic_x, old_topic_y])
                print(f"Unsubscribed from old topics for {self.last_known_device_id}")

            self.last_known_device_id = extracted_id

            # Clear the screen
            self.zone_squares.clear()
            self.trail_squares.clear()
            self.target_square_coords = None
            self._redraw_canvas()

            # If connected, subscribe to new topics
            if self.mqtt_client and self.mqtt_client.is_connected():
                self._subscribe_to_topics(self.mqtt_client)

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
        # Draw zones first
        for r, c in self.zone_squares:
            self._update_square_color(r, c)
        # Then draw trails over them if they overlap
        for r, c in self.trail_squares:
            self._update_square_color(r, c)
        # Finally, draw the target on top
        if self.target_square_coords:
            self._update_square_color(self.target_square_coords[0], self.target_square_coords[1])

    def _update_square_color(self, r, c):
        if not (0 <= r < GRID_DIMENSION and 0 <= c < GRID_DIMENSION):
            return

        is_target = (r, c) == self.target_square_coords
        is_trail = (r, c) in self.trail_squares
        is_zone = (r, c) in self.zone_squares
        item_id = self.colored_square_ids.get((r, c))

        if not is_target and not is_trail and not is_zone:
            if item_id:
                self.canvas.delete(item_id)
                del self.colored_square_ids[(r, c)]
            return

        # Determine color based on priority: target > trail > zone
        if is_target: color = "blue"
        elif is_trail: color = "red"
        elif is_zone: color = "orange"
        else: color = "white" # Should not happen based on logic above

        if item_id:
            self.canvas.itemconfig(item_id, fill=color)
        else:
            x1 = c * self.cell_pixel_size; y1 = r * self.cell_pixel_size
            x2 = x1 + self.cell_pixel_size; y2 = y1 + self.cell_pixel_size
            new_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
            self.colored_square_ids[(r, c)] = new_id

        # Ensure target and trail are always drawn on top of zones
        if is_target or is_trail:
            self.canvas.tag_raise(self.colored_square_ids.get((r, c)))

    def _connect_mqtt(self):
        self._disconnect_mqtt(); time.sleep(0.1)
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self._on_mqtt_connect
        self.mqtt_client.on_message = self._on_mqtt_message
        self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
        user = self.mqtt_user.get()
        if user: self.mqtt_client.username_pw_set(user, self.mqtt_pass.get())
        broker_address = self.mqtt_broker.get()
        if not broker_address: messagebox.showerror("Error", "MQTT Broker address cannot be empty."); return
        self.connection_status.set(f"Status: Connecting to {broker_address}...")
        try:
            self.mqtt_client.connect(broker_address, DEFAULT_MQTT_PORT, 60)
            self.mqtt_thread = threading.Thread(target=self.mqtt_client.loop_forever, daemon=True)
            self.mqtt_thread.start()
        except Exception as e:
            messagebox.showerror("MQTT Error", f"Could not connect to broker: {e}")
            self.connection_status.set("Status: Connection failed")

    def _disconnect_mqtt(self):
        if self.mqtt_client and self.mqtt_client.is_connected():
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            print("MQTT Disconnected.")
        # Clear target square on disconnect and redraw
        if self.target_square_coords:
            self.target_square_coords = None
            self._redraw_canvas()

    def _subscribe_to_topics(self, client):
        """Subscribes to MQTT topics based on the current device ID."""
        dev_id = self.device_id.get()
        if not dev_id:
            print("Cannot subscribe, Device ID is empty.")
            return
        topic_x = f"home/{dev_id}_tar_1_x/status"
        topic_y = f"home/{dev_id}_tar_1_y/status"
        client.subscribe([(topic_x, 0), (topic_y, 0)])
        print(f"Subscribed to:\n- {topic_x}\n- {topic_y}")

    def _on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("MQTT Connected Successfully."); self.connection_status.set("Status: Connected")
            self._subscribe_to_topics(client)
        else:
            error_messages = {1:"protocol version", 2:"client identifier", 3:"server unavailable", 4:"bad username/password", 5:"not authorised"}
            error_text = f"Failed to connect: {error_messages.get(rc, 'Unknown error')} (Code: {rc})"
            messagebox.showerror("MQTT Error", error_text); self.connection_status.set(f"Status: Failed")

    def _on_mqtt_disconnect(self, client, userdata, rc):
        self.connection_status.set("Status: Disconnected"); print(f"MQTT client disconnected with result code: {rc}")
        if self.target_square_coords:
            self.target_square_coords = None
            self._redraw_canvas()

    def _on_mqtt_message(self, client, userdata, msg):
        try:
            payload = float(msg.payload.decode())
            if "_tar_1_x" in msg.topic:
                self.current_x = payload; self._x_updated = True
            elif "_tar_1_y" in msg.topic:
                self.current_y = payload; self._y_updated = True
            if self._x_updated and self._y_updated:
                self._x_updated = False; self._y_updated = False
                self.master.after(0, self._update_target_on_grid)
        except (ValueError, UnicodeDecodeError) as e:
            print(f"Could not parse MQTT message payload: {msg.payload}. Error: {e}")

    def _update_target_on_grid(self):
        old_coords = self.target_square_coords
        if self.current_x == 0.0 and self.current_y == 0.0:
            self.target_square_coords = None
        else:
            col = int(((X_MAX - self.current_x) / (X_MAX - X_MIN)) * GRID_DIMENSION)
            row = int(((self.current_y - Y_MIN) / (Y_MAX - Y_MIN)) * GRID_DIMENSION)
            col = max(0, min(GRID_DIMENSION - 1, col))
            row = max(0, min(GRID_DIMENSION - 1, row))
            self.target_square_coords = (row, col)
            if self.trail_enabled.get(): self.trail_squares.add((row, col))

        # Redraw the whole canvas to ensure proper layering
        self._redraw_canvas()

    def _get_coords_from_event(self, event):
        c = int(event.x / self.cell_pixel_size); r = int(event.y / self.cell_pixel_size); return r, c

    def _on_canvas_press(self, event):
        if self.polygon_selection_active:
            self._add_polygon_point(event)
            return
        self.drag_start_pos = (event.x, event.y)

    def _on_canvas_drag(self, event):
        if self.polygon_selection_active: return
        if not self.drag_start_pos: return
        if self.drag_shape_id: self.canvas.delete(self.drag_shape_id)
        x1, y1 = self.drag_start_pos; x2, y2 = event.x, event.y
        if self.diagonal_mode.get(): vertices = self._get_rotated_rect_vertices(x1, y1, x2, y2)
        else: vertices = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
        self.drag_shape_id = self.canvas.create_polygon(vertices, outline="red", fill="", width=2)

    def _on_canvas_release(self, event):
        if self.polygon_selection_active: return
        if not self.drag_start_pos: return

        if self.drag_shape_id:
            self.canvas.delete(self.drag_shape_id); self.drag_shape_id = None
        x1, y1 = self.drag_start_pos; x2, y2 = event.x, event.y
        is_click = abs(x1 - x2) < 4 and abs(y1 - y2) < 4
        if self.diagonal_mode.get() and not is_click: vertices = self._get_rotated_rect_vertices(x1, y1, x2, y2)
        else: vertices = [(min(x1, x2), min(y1, y2)),(max(x1, x2), min(y1, y2)),(max(x1, x2), max(y1, y2)),(min(x1, x2), max(y1, y2))]
        min_x = min(v[0] for v in vertices); max_x = max(v[0] for v in vertices)
        min_y = min(v[1] for v in vertices); max_y = max(v[1] for v in vertices)
        start_r, start_c = self._get_coords_from_event(type('event', (), {'x': min_x, 'y': min_y})())
        end_r, end_c = self._get_coords_from_event(type('event', (), {'x': max_x, 'y': max_y})())
        is_right_click = event.num == 3
        use_add_mode = not self.add_mode.get() if is_right_click else self.add_mode.get()
        self.history_stack.append(self.zone_squares.copy())
        for r in range(start_r, end_r + 1):
            for c in range(start_c, end_c + 1):
                if not (0 <= r < GRID_DIMENSION and 0 <= c < GRID_DIMENSION): continue
                cell_center_x = (c + 0.5) * self.cell_pixel_size
                cell_center_y = (r + 0.5) * self.cell_pixel_size
                if self._is_point_in_polygon((cell_center_x, cell_center_y), vertices):
                    coords = (r, c)
                    if use_add_mode:
                        if coords not in self.zone_squares: self.zone_squares.add(coords); self._update_square_color(r, c)
                    else:
                        if coords in self.zone_squares: self.zone_squares.remove(coords); self._update_square_color(r, c)
        self.drag_start_pos = None

    def _get_rotated_rect_vertices(self, x_a, y_a, x_c, y_c):
        s_c = ((x_c - x_a) + (y_c - y_a)) / 2; t_c = ((x_c - x_a) - (y_c - y_a)) / 2
        x_b = x_a + t_c; y_b = y_a - t_c
        x_d = x_a + s_c; y_d = y_a + s_c
        return [(x_a, y_a), (x_b, y_b), (x_c, y_c), (x_d, y_d)]

    def _is_point_in_polygon(self, point, polygon_vertices):
        """Uses the Ray Casting algorithm to determine if a point is inside a polygon."""
        x, y = point
        n = len(polygon_vertices)
        inside = False
        p1x, p1y = polygon_vertices[0]
        for i in range(n + 1):
            p2x, p2y = polygon_vertices[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def _clear_zone(self):
        self.zone_squares.clear(); self._redraw_canvas(); print("Zone cleared.")

    def _clear_trail(self):
        self.trail_squares.clear(); self._redraw_canvas(); print("Movement trail cleared.")

    def _copy_template_to_clipboard(self):
        if not self.zone_squares: messagebox.showwarning("Empty Zone", "No zone is selected."); return
        template = self._generate_jinja_template()
        self.master.clipboard_clear(); self.master.clipboard_append(template); self.master.update()
        messagebox.showinfo("Success", "Home Assistant Jinja2 template copied to clipboard!")
    def _save_template_to_file(self):
        if not self.zone_squares: messagebox.showwarning("Empty Zone", "No zone is selected."); return
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if not filepath: return
        template = self._generate_jinja_template()
        try:
            with open(filepath, 'w') as f: f.write(template)
            messagebox.showinfo("Success", f"Zone template saved to {filepath}")
        except Exception as e: messagebox.showerror("Error", f"Failed to save file: {e}")
    def _load_zone_from_clipboard(self):
        try:
            template = self.master.clipboard_get()
            self._parse_and_load_zone(template)
        except tk.TclError: messagebox.showwarning("Clipboard Empty", "Clipboard does not contain text.")
        except Exception as e: messagebox.showerror("Parsing Error", f"Could not parse template from clipboard: {e}")
    def _load_zone_from_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if not filepath: return
        try:
            with open(filepath, 'r') as f: template = f.read()
            self._parse_and_load_zone(template)
        except Exception as e: messagebox.showerror("Error", f"Failed to load or parse file: {e}")

    # --- Polygon Methods ---
    def _toggle_polygon_mode(self):
        """Activates or deactivates the polygon selection mode."""
        self.polygon_selection_active = not self.polygon_selection_active
        if self.polygon_selection_active:
            self.polygon_button.config(relief=tk.SUNKEN)
            self.diagonal_mode.set(False) # Disable other modes
            self.diagonal_button.config(relief=tk.RAISED)
        else:
            self.polygon_button.config(relief=tk.RAISED)
            self._cancel_polygon_drawing()

    def _cancel_polygon_drawing(self):
        """Clears the current polygon drawing and deactivates the tool."""
        self._clear_current_polygon()
        if self.polygon_selection_active:
            self.polygon_selection_active = False
            self.polygon_button.config(relief=tk.RAISED)

    def _clear_current_polygon(self):
        """Clears the lines and vertices of the currently drawn polygon from the canvas."""
        if self.temp_line:
            self.canvas.delete(self.temp_line)
            self.temp_line = None
        for line_id in self.polygon_lines:
            self.canvas.delete(line_id)
        self.polygon_lines.clear()
        self.polygon_vertices.clear()

    def _add_polygon_point(self, event):
        point = (event.x, event.y)
        if self.polygon_vertices:
            last_point = self.polygon_vertices[-1]
            line_id = self.canvas.create_line(last_point, point, fill="green", width=2)
            self.polygon_lines.append(line_id)
        self.polygon_vertices.append(point)

    def _on_canvas_move(self, event):
        if not self.polygon_selection_active or not self.polygon_vertices:
            return
        if self.temp_line:
            self.canvas.delete(self.temp_line)
        last_point = self.polygon_vertices[-1]
        self.temp_line = self.canvas.create_line(last_point, (event.x, event.y), fill="green", width=2, dash=(4, 4))

    def _on_polygon_finish(self, event):
        if not self.polygon_selection_active or len(self.polygon_vertices) < 3:
            if self.polygon_selection_active and self.polygon_vertices:
                 messagebox.showwarning("Polygon Error", "A polygon requires at least 3 points.")
            self._cancel_polygon_drawing()
            return
        # Add the point from the double-click event to close the shape visually if needed.
        # However, the selection logic below uses the existing vertices list.
        self.history_stack.append(self.zone_squares.copy())
        vertices = self.polygon_vertices
        min_x = min(v[0] for v in vertices); max_x = max(v[0] for v in vertices)
        min_y = min(v[1] for v in vertices); max_y = max(v[1] for v in vertices)
        start_r, start_c = self._get_coords_from_event(type('event', (), {'x': min_x, 'y': min_y})())
        end_r, end_c = self._get_coords_from_event(type('event', (), {'x': max_x, 'y': max_y})())
        use_add_mode = self.add_mode.get()
        for r in range(start_r, end_r + 1):
            for c in range(start_c, end_c + 1):
                if not (0 <= r < GRID_DIMENSION and 0 <= c < GRID_DIMENSION): continue
                cell_center_x = (c + 0.5) * self.cell_pixel_size
                cell_center_y = (r + 0.5) * self.cell_pixel_size
                if self._is_point_in_polygon((cell_center_x, cell_center_y), vertices):
                    coords = (r, c)
                    if use_add_mode:
                        if coords not in self.zone_squares: self.zone_squares.add(coords); self._update_square_color(r, c)
                    else:
                        if coords in self.zone_squares: self.zone_squares.remove(coords); self._update_square_color(r, c)

        # Clear the completed polygon, but keep the tool active.
        self._clear_current_polygon()
        print("Polygon selection applied. Ready for next polygon.")

    def _undo_polygon_point(self):
        if not self.polygon_vertices: return
        self.polygon_vertices.pop()
        if self.polygon_lines:
            line_to_remove = self.polygon_lines.pop()
            self.canvas.delete(line_to_remove)
        if not self.polygon_vertices and self.temp_line:
            self.canvas.delete(self.temp_line)
            self.temp_line = None

    def _parse_and_load_zone(self, template):
        """Robustly parses a single-line Jinja2 template string to populate the zone."""
        new_zone = set()
        main_condition_match = re.search(r"\{\{\s*(.*?)\s*\}\}", template, re.DOTALL)
        if not main_condition_match:
            raise ValueError("Could not find main condition block {{ ... }} in template.")
        full_condition_str = " ".join(main_condition_match.group(1).split())
        row_conditions = []
        paren_level = 0; last_split_idx = 0
        for i in range(len(full_condition_str) - 3):
            char = full_condition_str[i]
            if char == '(': paren_level += 1
            elif char == ')': paren_level -= 1
            if full_condition_str[i:i+4] == ' or ' and paren_level == 0:
                row_conditions.append(full_condition_str[last_split_idx:i])
                last_split_idx = i + 4
        row_conditions.append(full_condition_str[last_split_idx:])
        y_pattern = re.compile(r"y >= ([\d\.-]+)")
        x_pattern = re.compile(r"x >= ([\d\.-]+) and x < ([\d\.-]+)")
        for row_str in row_conditions:
            y_match = y_pattern.search(row_str)
            if not y_match: continue
            y_lower = float(y_match.group(1))
            r = round(y_lower / CELL_RESOLUTION)
            for x_match in x_pattern.finditer(row_str):
                x_lower, x_upper = map(float, x_match.groups())
                c_start = round(((X_MAX - x_upper) / (X_MAX - X_MIN)) * GRID_DIMENSION)
                c_end = round(((X_MAX - x_lower) / (X_MAX - X_MIN)) * GRID_DIMENSION)
                for c in range(c_start, c_end):
                    if 0 <= r < GRID_DIMENSION and 0 <= c < GRID_DIMENSION: new_zone.add((r, c))
        if not new_zone: raise ValueError("No valid zone conditions found in the template.")
        self.zone_squares = new_zone
        self._redraw_canvas()
        messagebox.showinfo("Success", f"Loaded {len(new_zone)} squares into the zone.")

    def _generate_jinja_template(self):
        """Generates a clean, single-line Jinja2 template."""
        if not self.zone_squares: return ""
        rows = {}
        for r, c in self.zone_squares: rows.setdefault(r, []).append(c)
        row_conditions = []
        for r, cols in sorted(rows.items()):
            cols.sort()
            y_lower = r * CELL_RESOLUTION; y_upper = (r + 1) * CELL_RESOLUTION
            if not cols: continue
            segments = []; start_of_segment = cols[0]
            for i in range(1, len(cols)):
                if cols[i] != cols[i-1] + 1: segments.append((start_of_segment, cols[i-1])); start_of_segment = cols[i]
            segments.append((start_of_segment, cols[-1]))
            x_conditions = []
            for c_min, c_max in segments:
                x_upper = X_MAX - (c_min * CELL_RESOLUTION); x_lower = X_MAX - ((c_max + 1) * CELL_RESOLUTION)
                x_conditions.append(f"(x >= {x_lower:.2f} and x < {x_upper:.2f})")
            x_condition_str = " or ".join(x_conditions)
            row_conditions.append(f"((y >= {y_lower:.2f} and y < {y_upper:.2f}) and ({x_condition_str}))")
        full_condition_str = " or ".join(row_conditions)
        return f"""{{% set x = states('{self.get_sensor_entity_id('x')}') | float(0) %}}
{{% set y = states('{self.get_sensor_entity_id('y')}') | float(0) %}}
{{{{ {full_condition_str} }}}}"""

    def get_sensor_entity_id(self, axis):
        axis_map = {'x': 7, 'y': 8}
        return f"sensor.lnlinkha_{self.device_id.get()}_{axis_map[axis]}"

    def _on_closing(self):
        self._save_settings()
        print("Closing application...")
        self._disconnect_mqtt()
        self.master.destroy()


# --- Main Execution ---
if __name__ == "__main__":
    try:
        if 'pyi_splash' in os.environ:
             import pyi_splash
             pyi_splash.update_text('UI Initializing...')
             pyi_splash.close()
        root = tk.Tk()
        app = MMWaveVisualizer(root)
        root.mainloop()
    except Exception as e:
        # --- CORRECTED ERROR HANDLING ---
        # Use a messagebox for GUI apps instead of print/input
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw() # Hide the empty root window
        messagebox.showerror("Fatal Error", f"An unexpected error occurred:\n\n{e}")
        root.destroy()
