# unified_time_weather_final.py
# Fixed Dark/Light mode, Add Button, and Dynamic Attractions

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import pytz
import math
import requests
import threading

# ----------------------------
# Configuration
# ----------------------------
API_KEY = "36abdcf0e351140d2f07f648d4a6ce83"

# Base cities
CITY_TIMEZONES = {
    "Mumbai": "Asia/Kolkata",
    "Bengaluru": "Asia/Kolkata",
    "New York": "America/New_York",
    "London": "Europe/London",
    "Tokyo": "Asia/Tokyo",
    "Toronto": "America/Toronto",
}

# Pre-defined database for specific attractions
PLACE_RECOMMENDATIONS = {
    "Mumbai": "Enjoy Marine Drive!",
    "Bengaluru": "Visit Lalbagh Botanical Garden.",
    "New York": "Times Square is lively at night.",
    "London": "Explore the Tower Bridge.",
    "Tokyo": "Visit Shibuya Crossing at night.",
    "Sydney": "Enjoy the Opera House!",
    "Dubai": "Visit the Burj Khalifa!",
    "Paris": "Eiffel Tower is great at sunset.",
    "Toronto": "Visit the CN Tower.",
}

AVAILABLE_ZONES = {
    "Mumbai (IST)": "Asia/Kolkata",
    "Bengaluru (IST)": "Asia/Kolkata",
    "New York (EST/EDT)": "America/New_York",
    "London (GMT)": "Europe/London",
    "Tokyo (JST)": "Asia/Tokyo",
    "Sydney (AEST/AEDT)": "Australia/Sydney",
}

# ----------------------------
# Helpers for weather
# ----------------------------
def _call_owm(url, params):
    params = params.copy()
    params['appid'] = API_KEY
    params.setdefault('units', 'metric')
    resp = requests.get(url, params=params, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(f"Weather error: {resp.status_code}")
    return resp.json()

def get_weather_now(city):
    url = "https://api.openweathermap.org/data/2.5/weather"
    data = _call_owm(url, {"q": city})
    return {
        'name': data.get('name') or city,
        'country': data.get('sys', {}).get('country', ''),
        'temp': data.get('main', {}).get('temp'),
        'feels_like': data.get('main', {}).get('feels_like'),
        'humidity': data.get('main', {}).get('humidity'),
        'wind_speed': data.get('wind', {}).get('speed'),
        'condition_desc': data.get('weather', [{}])[0].get('description'),
        'lat': data.get('coord', {}).get('lat'),
        'lon': data.get('coord', {}).get('lon'),
    }

def get_weather_forecast_by_coords(lat, lon, days=3):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    data = _call_owm(url, {"lat": lat, "lon": lon})
    entries = data.get('list', [])
    results = []
    for i in range(0, min(len(entries), days * 8), 8):
        it = entries[i]
        results.append({
            'date': datetime.fromtimestamp(it['dt']).date(),
            'temp_avg': it['main']['temp'],
            'condition': it['weather'][0]['main']
        })
    return results

# ----------------------------
# Main App
# ----------------------------
class UnifiedApp:
    def __init__(self, root):
        self.root = root
        root.title("Unified Time & Weather App")
        root.geometry("1200x720")

        self.dark_mode = None  # Force initial theme application
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Layout Frames
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(side="top", fill="both", expand=True)

        self.left_frame = tk.Frame(self.top_frame)
        self.right_frame = tk.Frame(self.top_frame)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.bottom_frame = tk.Frame(root, height=180)
        self.bottom_frame.pack(side="bottom", fill="x", padx=10, pady=6)
        self.bottom_frame.pack_propagate(False)

        # Build UI Components
        self._build_main_clock_panel(self.left_frame)
        self._build_worldclock_panel(self.left_frame)
        self._build_weather_panel(self.right_frame)
        self._build_analog_clocks(self.bottom_frame)

        # Start background loops
        self._update_main_clock_once()
        self._update_analog_clocks()
        self._start_world_clock_loop()

    def _build_main_clock_panel(self, parent):
        self.greet_lbl = tk.Label(parent, text="", font=("Helvetica", 20, "bold"))
        self.greet_lbl.pack(anchor="w")
        self.time_lbl = tk.Label(parent, text="--:--:--", font=("Courier New", 48, "bold"))
        self.time_lbl.pack(anchor="w")
        self.date_lbl = tk.Label(parent, text="", font=("Helvetica", 12))
        self.date_lbl.pack(anchor="w", pady=(2,8))

        tk.Label(parent, text="Main Clock Time Zone:", font=("Helvetica", 10)).pack(anchor="w")
        self.main_tz_var = tk.StringVar(value="Mumbai (IST)")
        self.main_tz_menu = ttk.OptionMenu(parent, self.main_tz_var, "Mumbai (IST)", *AVAILABLE_ZONES.keys(), command=self._on_zone_change)
        self.main_tz_menu.pack(anchor="w", pady=4)

        self.diff_lbl = tk.Label(parent, text="", font=("Helvetica", 10))
        self.diff_lbl.pack(anchor="w", pady=(4,8))

    def _on_zone_change(self, selection):
        self._apply_theme_for_selection(selection)

    def _update_main_clock_once(self):
        label = self.main_tz_var.get()
        tzname = AVAILABLE_ZONES.get(label, "Asia/Kolkata")
        try:
            now = datetime.now(pytz.timezone(tzname))
        except:
            now = datetime.now()
            
        self.time_lbl.config(text=now.strftime("%H:%M:%S"))
        self.date_lbl.config(text=now.strftime("%A, %d %B %Y"))
        self.greet_lbl.config(text=self._get_greeting(now.hour))
        
        # Check if theme needs to change based on selected timezone hour
        self._apply_theme_for_selection(label)
        self.root.after(1000, self._update_main_clock_once)

    def _get_greeting(self, hour):
        if 5 <= hour < 12: return "Good Morning"
        if 12 <= hour < 17: return "Good Afternoon"
        if 17 <= hour < 21: return "Good Evening"
        return "Good Night"

    def _build_worldclock_panel(self, parent):
        frame = tk.Frame(parent)
        frame.pack(fill="both", expand=True, pady=6)
        tk.Label(frame, text="World Clocks & Suggestions", font=("Helvetica", 12, "bold")).pack(anchor="w")

        add_row = tk.Frame(frame)
        add_row.pack(fill="x", pady=4)
        tk.Label(add_row, text="Add Place:").pack(side="left")
        self.new_city_name = tk.StringVar()
        ttk.Entry(add_row, textvariable=self.new_city_name, width=15).pack(side="left", padx=5)

        tk.Label(add_row, text="TZ:").pack(side="left")
        self.new_city_tz = tk.StringVar()
        self.tz_cb = ttk.Combobox(add_row, textvariable=self.new_city_tz, values=pytz.common_timezones, width=20)
        self.tz_cb.pack(side="left", padx=5)
        ttk.Button(add_row, text="Add", command=self._add_custom_city).pack(side="left", padx=5)

        self.wc_text = tk.Text(frame, height=10, wrap="word")
        self.wc_text.pack(fill="both", expand=True)

    def _add_custom_city(self):
        city = self.new_city_name.get().strip()
        tz = self.new_city_tz.get().strip()
        if city and tz:
            try:
                pytz.timezone(tz)
                CITY_TIMEZONES[city] = tz
                # Dynamic attraction logic as requested
                if city not in PLACE_RECOMMENDATIONS:
                    PLACE_RECOMMENDATIONS[city] = f"Explore the local culture and landmarks in {city}!"
                
                self._refresh_world_clocks()
                self.new_city_name.set("")
                self.new_city_tz.set("")
            except:
                self.wc_text.insert(tk.END, f"\nError: Invalid Timezone '{tz}'\n")

    def _refresh_world_clocks(self):
        self.wc_text.delete("1.0", tk.END)
        for city, tz in CITY_TIMEZONES.items():
            try:
                now = datetime.now(pytz.timezone(tz))
                greet = self._get_greeting(now.hour)
                sugg = PLACE_RECOMMENDATIONS.get(city, "Enjoy your day!")
                self.wc_text.insert(tk.END, f"{city} — {now.strftime('%H:%M:%S')}\n  {greet} | {sugg}\n\n")
            except: pass

    def _start_world_clock_loop(self):
        self._refresh_world_clocks()
        self.root.after(5000, self._start_world_clock_loop)

    def _build_weather_panel(self, parent):
        tk.Label(parent, text="Weather & Forecast", font=("Helvetica", 14, "bold")).pack(anchor="w")
        ctrl = tk.Frame(parent)
        ctrl.pack(fill="x", pady=4)
        self.city_var = tk.StringVar(value="Mumbai")
        ttk.Entry(ctrl, textvariable=self.city_var).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(ctrl, text="Fetch", command=self.fetch_weather).pack(side="left", padx=6)
        self.weather_output = tk.Text(parent, height=18, wrap="word")
        self.weather_output.pack(fill="both", expand=True, pady=6)

    def fetch_weather(self):
        city = self.city_var.get().strip()
        if not city: return
        threading.Thread(target=self._weather_thread, args=(city,), daemon=True).start()

    def _weather_thread(self, city):
        try:
            now = get_weather_now(city)
            lines = [f"{now['name']}, {now['country']}", f"{now['condition_desc'].title()}", 
                     f"Temp: {now['temp']}°C", f"Humidity: {now['humidity']}%", "", "Forecast (3 days):"]
            fc = get_weather_forecast_by_coords(now['lat'], now['lon'])
            for d in fc:
                lines.append(f"{d['date']}: {d['temp_avg']}°C — {d['condition']}")
            self.root.after(0, lambda: self._set_weather_text("\n".join(lines)))
        except:
            self.root.after(0, lambda: self._set_weather_text("Error fetching weather."))

    def _set_weather_text(self, text):
        self.weather_output.delete("1.0", tk.END)
        self.weather_output.insert(tk.END, text)

    def _build_analog_clocks(self, parent):
        self.analog_list = []
        frame = tk.Frame(parent)
        frame.pack(fill="x", padx=6, pady=6)
        zones = ["Asia/Kolkata", "America/New_York", "Europe/London", "Asia/Tokyo"]
        for tz in zones:
            f = tk.Frame(frame, padx=8); f.pack(side="left")
            tk.Label(f, text=tz).pack()
            c = tk.Canvas(f, width=150, height=150); c.pack()
            self.analog_list.append((c, tz))

    def _update_analog_clocks(self):
        for canvas, tz in self.analog_list:
            try:
                now = datetime.now(pytz.timezone(tz))
                self._draw_analog(canvas, now)
            except: pass
        self.root.after(1000, self._update_analog_clocks)

    def _draw_analog(self, canvas, now):
        canvas.delete("all")
        x, y, r = 75, 75, 60
        main_color = "#e6e6e6" if self.dark_mode else "black"
        canvas.create_oval(x-r, y-r, x+r, y+r, width=2, outline=main_color)
        hr, mn, sc = now.hour % 12, now.minute, now.second
        hr_a = math.radians((hr*30) + (mn*0.5) - 90)
        mn_a = math.radians((mn*6) - 90)
        sc_a = math.radians((sc*6) - 90)
        canvas.create_line(x, y, x + 30*math.cos(hr_a), y + 30*math.sin(hr_a), width=3, fill=main_color)
        canvas.create_line(x, y, x + 45*math.cos(mn_a), y + 45*math.sin(mn_a), width=2, fill=main_color)
        canvas.create_line(x, y, x + 55*math.cos(sc_a), y + 55*math.sin(sc_a), fill="red", width=1)

    # ----------------------------
    # Theme Logic
    # ----------------------------
    def _apply_theme_for_selection(self, selected_label):
        tzname = AVAILABLE_ZONES.get(selected_label, "Asia/Kolkata")
        try:
            hour = datetime.now(pytz.timezone(tzname)).hour
        except:
            hour = datetime.now().hour
        
        # Dark mode between 6 PM and 6 AM
        is_night = not (6 <= hour < 18)
        
        if self.dark_mode != is_night:
            if is_night: self._apply_darkmode()
            else: self._apply_lightmode()

    def _apply_darkmode(self):
        self.dark_mode = True
        bg, fg, accent = "#2b2b2b", "#e6e6e6", "#3c3f41"
        
        self.style.configure("TFrame", background=bg)
        self.style.configure("TLabel", background=bg, foreground=fg)
        self.style.configure("TButton", background=accent, foreground=fg)
        self.style.configure("TEntry", fieldbackground=accent, foreground=fg, insertcolor=fg)
        self.style.configure("TCombobox", fieldbackground=accent, background=bg, foreground=fg, arrowcolor=fg)
        self.style.map("TCombobox", fieldbackground=[('readonly', accent)], foreground=[('readonly', fg)])

        self.root.configure(bg=bg)
        self._set_widget_colors(self.root, bg, fg, accent)

    def _apply_lightmode(self):
        self.dark_mode = False
        bg, fg, accent = "#f7f7f7", "#000000", "white"
        
        self.style.configure("TFrame", background=bg)
        self.style.configure("TLabel", background=bg, foreground=fg)
        self.style.configure("TButton", background="#e1e1e1", foreground=fg)
        self.style.configure("TEntry", fieldbackground=accent, foreground=fg, insertcolor=fg)
        self.style.configure("TCombobox", fieldbackground=accent, background=bg, foreground=fg, arrowcolor=fg)
        self.style.map("TCombobox", fieldbackground=[('readonly', accent)], foreground=[('readonly', fg)])

        self.root.configure(bg=bg)
        self._set_widget_colors(self.root, bg, fg, accent)

    def _set_widget_colors(self, widget, bg, fg, accent):
        try:
            cls = widget.winfo_class()
            if cls in ("Frame", "LabelFrame", "TFrame"):
                widget.configure(bg=bg)
            elif cls == "Label":
                widget.configure(bg=bg, fg=fg)
            elif cls == "Text":
                widget.configure(bg=accent, fg=fg, insertbackground=fg, padx=5, pady=5)
            elif cls == "Canvas":
                widget.configure(bg=accent, highlightthickness=0)
            elif cls == "Entry": # tk.Entry
                widget.configure(bg=accent, fg=fg, insertbackground=fg)
            elif cls == "Button": # tk.Button
                widget.configure(bg=bg, fg=fg)
        except: pass
        
        for child in widget.winfo_children():
            self._set_widget_colors(child, bg, fg, accent)

if __name__ == "__main__":
    root = tk.Tk()
    app = UnifiedApp(root)
    root.mainloop()

