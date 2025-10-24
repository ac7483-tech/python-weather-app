import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import requests
import datetime
import json
import time

class WeatherApp:
    def __init__(self, master):
        self.master = master
        master.title("Advanced Weather Dashboard")
        master.geometry("1200x800")
        master.resizable(True, True)

        self.api_key = "YOUR_API_KEY_HERE"
        self.base_url_current = "http://api.openweathermap.org/data/2.5/weather?"
        self.base_url_forecast = "http://api.openweathermap.org/data/2.5/forecast?"

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#e0f7fa")
        self.style.configure("TLabel", background="#e0f7fa", font=("Helvetica", 12))
        self.style.configure("TButton", font=("Helvetica", 12, "bold"), background="#00796b", foreground="white")
        self.style.map("TButton", background=[('active', '#004d40')])
        self.style.configure("Header.TLabel", font=("Helvetica", 18, "bold"), foreground="#004d40")
        self.style.configure("Large.TLabel", font=("Helvetica", 14, "bold"), foreground="#263238")

        self.main_frame = ttk.Frame(master, padding="20 20 20 20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_input_section()
        self.create_current_weather_section()
        self.create_hourly_forecast_section()
        self.create_daily_forecast_section()
        self.create_additional_info_section()
        self.create_status_bar()

        self.update_clock()
        self.update_weather_periodically()

    def create_input_section(self):
        self.input_frame = ttk.Frame(self.main_frame, padding="10 10 10 10", relief=tk.RAISED, borderwidth=2)
        self.input_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")

        self.city_label = ttk.Label(self.input_frame, text="Enter City Name:")
        self.city_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.city_entry = ttk.Entry(self.input_frame, width=40, font=("Helvetica", 12))
        self.city_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.city_entry.bind("<Return>", self.fetch_weather_on_enter)

        self.fetch_button = ttk.Button(self.input_frame, text="Fetch Weather", command=self.fetch_weather_data)
        self.fetch_button.grid(row=0, column=2, padx=10, pady=5)

        self.last_updated_label = ttk.Label(self.input_frame, text="Last Updated: Never")
        self.last_updated_label.grid(row=0, column=3, padx=10, pady=5, sticky="e")

        self.input_frame.grid_columnconfigure(1, weight=1)
        self.input_frame.grid_columnconfigure(3, weight=1)

    def create_current_weather_section(self):
        self.current_weather_frame = ttk.Frame(self.main_frame, padding="10 10 10 10", relief=tk.GROOVE, borderwidth=2)
        self.current_weather_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.current_header = ttk.Label(self.current_weather_frame, text="Current Weather", style="Header.TLabel")
        self.current_header.grid(row=0, column=0, columnspan=2, pady=10)

        self.location_label = ttk.Label(self.current_weather_frame, text="Location: N/A", style="Large.TLabel")
        self.location_label.grid(row=1, column=0, columnspan=2, pady=5)

        self.temperature_label = ttk.Label(self.current_weather_frame, text="Temp: N/A", style="Large.TLabel")
        self.temperature_label.grid(row=2, column=0, columnspan=2, pady=5)

        self.feels_like_label = ttk.Label(self.current_weather_frame, text="Feels Like: N/A")
        self.feels_like_label.grid(row=3, column=0, columnspan=2, pady=2)

        self.description_label = ttk.Label(self.current_weather_frame, text="Description: N/A")
        self.description_label.grid(row=4, column=0, columnspan=2, pady=2)

        self.humidity_label = ttk.Label(self.current_weather_frame, text="Humidity: N/A")
        self.humidity_label.grid(row=5, column=0, padx=5, pady=2, sticky="w")

        self.wind_speed_label = ttk.Label(self.current_weather_frame, text="Wind: N/A")
        self.wind_speed_label.grid(row=5, column=1, padx=5, pady=2, sticky="e")

        self.pressure_label = ttk.Label(self.current_weather_frame, text="Pressure: N/A")
        self.pressure_label.grid(row=6, column=0, padx=5, pady=2, sticky="w")

        self.visibility_label = ttk.Label(self.current_weather_frame, text="Visibility: N/A")
        self.visibility_label.grid(row=6, column=1, padx=5, pady=2, sticky="e")

        self.sunrise_label = ttk.Label(self.current_weather_frame, text="Sunrise: N/A")
        self.sunrise_label.grid(row=7, column=0, padx=5, pady=2, sticky="w")

        self.sunset_label = ttk.Label(self.current_weather_frame, text="Sunset: N/A")
        self.sunset_label.grid(row=7, column=1, padx=5, pady=2, sticky="e")

        self.min_max_temp_label = ttk.Label(self.current_weather_frame, text="Min/Max Temp: N/A")
        self.min_max_temp_label.grid(row=8, column=0, columnspan=2, pady=5)

        self.weather_icon_label = ttk.Label(self.current_weather_frame, text="Weather Icon")
        self.weather_icon_label.grid(row=9, column=0, columnspan=2, pady=5)

        self.current_weather_frame.grid_columnconfigure(0, weight=1)
        self.current_weather_frame.grid_columnconfigure(1, weight=1)

    def create_hourly_forecast_section(self):
        self.hourly_forecast_frame = ttk.Frame(self.main_frame, padding="10 10 10 10", relief=tk.GROOVE, borderwidth=2)
        self.hourly_forecast_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.hourly_header = ttk.Label(self.hourly_forecast_frame, text="Hourly Forecast (Next 24h)", style="Header.TLabel")
        self.hourly_header.grid(row=0, column=0, columnspan=4, pady=10)

        self.hourly_frames = []
        for i in range(8):
            frame = ttk.Frame(self.hourly_forecast_frame, relief=tk.SUNKEN, borderwidth=1, padding="5 5 5 5")
            frame.grid(row=1 + i // 4, column=i % 4, padx=5, pady=5, sticky="nsew")

            time_lbl = ttk.Label(frame, text="Time: N/A", font=("Helvetica", 10, "bold"))
            time_lbl.pack(pady=1)
            temp_lbl = ttk.Label(frame, text="Temp: N/A")
            temp_lbl.pack(pady=1)
            desc_lbl = ttk.Label(frame, text="Desc: N/A")
            desc_lbl.pack(pady=1)
            humidity_lbl = ttk.Label(frame, text="Hum: N/A")
            humidity_lbl.pack(pady=1)

            self.hourly_frames.append({
                "frame": frame,
                "time": time_lbl,
                "temp": temp_lbl,
                "desc": desc_lbl,
                "humidity": humidity_lbl
            })
            frame.grid_columnconfigure(0, weight=1)

        for i in range(4):
            self.hourly_forecast_frame.grid_columnconfigure(i, weight=1)
        for i in range(1, 1 + 8 // 4 + 1):
            self.hourly_forecast_frame.grid_rowconfigure(i, weight=1)

    def create_daily_forecast_section(self):
        self.daily_forecast_frame = ttk.Frame(self.main_frame, padding="10 10 10 10", relief=tk.GROOVE, borderwidth=2)
        self.daily_forecast_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        self.daily_header = ttk.Label(self.daily_forecast_frame, text="Daily Forecast (Next 5 Days)", style="Header.TLabel")
        self.daily_header.grid(row=0, column=0, columnspan=5, pady=10)

        self.daily_frames = []
        for i in range(5):
            frame = ttk.Frame(self.daily_forecast_frame, relief=tk.SUNKEN, borderwidth=1, padding="5 5 5 5")
            frame.grid(row=1, column=i, padx=5, pady=5, sticky="nsew")

            day_lbl = ttk.Label(frame, text="Day: N/A", font=("Helvetica", 10, "bold"))
            day_lbl.pack(pady=1)
            temp_max_lbl = ttk.Label(frame, text="Max Temp: N/A")
            temp_max_lbl.pack(pady=1)
            temp_min_lbl = ttk.Label(frame, text="Min Temp: N/A")
            temp_min_lbl.pack(pady=1)
            desc_lbl = ttk.Label(frame, text="Desc: N/A")
            desc_lbl.pack(pady=1)

            self.daily_frames.append({
                "frame": frame,
                "day": day_lbl,
                "temp_max": temp_max_lbl,
                "temp_min": temp_min_lbl,
                "desc": desc_lbl
            })
            frame.grid_columnconfigure(0, weight=1)

        for i in range(5):
            self.daily_forecast_frame.grid_columnconfigure(i, weight=1)
        self.daily_forecast_frame.grid_rowconfigure(1, weight=1)

    def create_additional_info_section(self):
        self.additional_info_frame = ttk.Frame(self.main_frame, padding="10 10 10 10", relief=tk.GROOVE, borderwidth=2)
        self.additional_info_frame.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

        self.additional_header = ttk.Label(self.additional_info_frame, text="Additional Information", style="Header.TLabel")
        self.additional_header.grid(row=0, column=0, columnspan=2, pady=10)

        self.cloudiness_label = ttk.Label(self.additional_info_frame, text="Cloudiness: N/A")
        self.cloudiness_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")

        self.gust_speed_label = ttk.Label(self.additional_info_frame, text="Wind Gust: N/A")
        self.gust_speed_label.grid(row=1, column=1, padx=5, pady=2, sticky="e")

        self.sea_level_label = ttk.Label(self.additional_info_frame, text="Sea Level: N/A")
        self.sea_level_label.grid(row=2, column=0, padx=5, pady=2, sticky="w")

        self.ground_level_label = ttk.Label(self.additional_info_frame, text="Ground Level: N/A")
        self.ground_level_label.grid(row=2, column=1, padx=5, pady=2, sticky="e")

        self.coordinates_label = ttk.Label(self.additional_info_frame, text="Coordinates: N/A")
        self.coordinates_label.grid(row=3, column=0, columnspan=2, padx=5, pady=2, sticky="w")

        self.time_zone_label = ttk.Label(self.additional_info_frame, text="Time Zone Offset: N/A")
        self.time_zone_label.grid(row=4, column=0, columnspan=2, padx=5, pady=2, sticky="w")

        self.info_placeholder_one = ttk.Label(self.additional_info_frame, text="Extended Data Point 1: N/A")
        self.info_placeholder_one.grid(row=5, column=0, padx=5, pady=2, sticky="w")

        self.info_placeholder_two = ttk.Label(self.additional_info_frame, text="Extended Data Point 2: N/A")
        self.info_placeholder_two.grid(row=5, column=1, padx=5, pady=2, sticky="e")

        self.info_placeholder_three = ttk.Label(self.additional_info_frame, text="Extended Data Point 3: N/A")
        self.info_placeholder_three.grid(row=6, column=0, padx=5, pady=2, sticky="w")

        self.info_placeholder_four = ttk.Label(self.additional_info_frame, text="Extended Data Point 4: N/A")
        self.info_placeholder_four.grid(row=6, column=1, padx=5, pady=2, sticky="e")

        self.additional_info_frame.grid_columnconfigure(0, weight=1)
        self.additional_info_frame.grid_columnconfigure(1, weight=1)

    def create_status_bar(self):
        self.status_bar = ttk.Frame(self.master, relief=tk.SUNKEN, borderwidth=1)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_message = ttk.Label(self.status_bar, text="Ready", anchor=tk.W, font=("Helvetica", 10))
        self.status_message.pack(side=tk.LEFT, padx=10, pady=2)

        self.current_time_label = ttk.Label(self.status_bar, text="Time: N/A", anchor=tk.E, font=("Helvetica", 10))
        self.current_time_label.pack(side=tk.RIGHT, padx=10, pady=2)

    def fetch_weather_on_enter(self, event=None):
        self.fetch_weather_data()

    def fetch_weather_data(self):
        city = self.city_entry.get()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name.")
            self.update_status("Error: No city entered.")
            return

        self.update_status(f"Fetching weather for {city}...")
        self.master.update_idletasks()

        current_weather_params = {"q": city, "appid": self.api_key, "units": "metric"}
        forecast_params = {"q": city, "appid": self.api_key, "units": "metric", "cnt": 40}

        try:
            current_response = requests.get(self.base_url_current, params=current_weather_params)
            current_response.raise_for_status()
            current_data = current_response.json()

            forecast_response = requests.get(self.base_url_forecast, params=forecast_params)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()

            if current_data["cod"] == 200 and forecast_data["cod"] == "200":
                self.update_current_weather(current_data)
                self.update_hourly_forecast(forecast_data)
                self.update_daily_forecast(forecast_data)
                self.update_additional_info(current_data)
                self.update_last_updated()
                self.update_status(f"Weather data loaded for {city}.")
            else:
                error_message = current_data.get("message", "Unknown error")
                messagebox.showerror("API Error", f"Could not fetch weather data for {city}. Error: {error_message}")
                self.update_status(f"API Error for {city}.")

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                messagebox.showerror("City Not Found", f"Could not find weather data for '{city}'. Please check the city name.")
                self.update_status(f"Error: City '{city}' not found.")
            else:
                messagebox.showerror("Network Error", f"HTTP Error: {e}")
                self.update_status(f"Network Error: {e.response.status_code}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Network Error", "Could not connect to the weather service. Please check your internet connection.")
            self.update_status("Error: No internet connection.")
        except requests.exceptions.Timeout:
            messagebox.showerror("Network Error", "Request to weather service timed out.")
            self.update_status("Error: Request timed out.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Request Error", f"An unexpected error occurred: {e}")
            self.update_status(f"Unexpected Request Error: {e}")
        except json.JSONDecodeError:
            messagebox.showerror("Data Error", "Could not decode weather data. Invalid JSON response.")
            self.update_status("Error: Invalid JSON response.")
        except KeyError as e:
            messagebox.showerror("Data Parsing Error", f"Missing expected data in API response: {e}")
            self.update_status(f"Error: Missing API data: {e}.")
        except Exception as e:
            messagebox.showerror("Application Error", f"An unexpected application error occurred: {e}")
            self.update_status(f"Unexpected Application Error: {e}.")

    def update_current_weather(self, data):
        location = f"{data['name']}, {data['sys']['country']}"
        temp = f"{data['main']['temp']:.1f}°C"
        feels_like = f"{data['main']['feels_like']:.1f}°C"
        description = data['weather'][0]['description'].capitalize()
        humidity = f"{data['main']['humidity']}%"
        wind_speed = f"{data['wind']['speed']:.1f} m/s"
        pressure = f"{data['main']['pressure']} hPa"
        visibility = f"{data['visibility'] / 1000:.1f} km"
        min_temp = f"{data['main']['temp_min']:.1f}°C"
        max_temp = f"{data['main']['temp_max']:.1f}°C"

        sunrise_ts = data['sys']['sunrise'] + data['timezone']
        sunset_ts = data['sys']['sunset'] + data['timezone']
        utc_offset = data['timezone']

        sunrise_time = datetime.datetime.fromtimestamp(sunrise_ts, tz=datetime.timezone.utc).strftime('%H:%M')
        sunset_time = datetime.datetime.fromtimestamp(sunset_ts, tz=datetime.timezone.utc).strftime('%H:%M')

        self.location_label.config(text=f"Location: {location}")
        self.temperature_label.config(text=f"Temperature: {temp}")
        self.feels_like_label.config(text=f"Feels Like: {feels_like}")
        self.description_label.config(text=f"Description: {description}")
        self.humidity_label.config(text=f"Humidity: {humidity}")
        self.wind_speed_label.config(text=f"Wind: {wind_speed}")
        self.pressure_label.config(text=f"Pressure: {pressure}")
        self.visibility_label.config(text=f"Visibility: {visibility}")
        self.sunrise_label.config(text=f"Sunrise: {sunrise_time}")
        self.sunset_label.config(text=f"Sunset: {sunset_time}")
        self.min_max_temp_label.config(text=f"Min/Max Temp: {min_temp} / {max_temp}")
        self.weather_icon_label.config(text=f"Icon: {data['weather'][0]['icon']}")

    def update_hourly_forecast(self, data):
        for i, hourly_frame_data in enumerate(self.hourly_frames):
            if i < len(data['list']):
                forecast_item = data['list'][i]
                dt_object = datetime.datetime.fromtimestamp(forecast_item['dt'], tz=datetime.timezone.utc)
                offset_seconds = data['city']['timezone']
                local_dt_object = dt_object + datetime.timedelta(seconds=offset_seconds)

                hourly_frame_data['time'].config(text=local_dt_object.strftime("%H:%M"))
                hourly_frame_data['temp'].config(text=f"{forecast_item['main']['temp']:.1f}°C")
                hourly_frame_data['desc'].config(text=forecast_item['weather'][0]['description'].capitalize())
                hourly_frame_data['humidity'].config(text=f"{forecast_item['main']['humidity']}%")
            else:
                hourly_frame_data['time'].config(text="N/A")
                hourly_frame_data['temp'].config(text="N/A")
                hourly_frame_data['desc'].config(text="N/A")
                hourly_frame_data['humidity'].config(text="N/A")

    def update_daily_forecast(self, data):
        daily_temps = {}
        offset_seconds = data['city']['timezone']

        for item in data['list']:
            dt_object = datetime.datetime.fromtimestamp(item['dt'], tz=datetime.timezone.utc)
            local_dt_object = dt_object + datetime.timedelta(seconds=offset_seconds)
            day = local_dt_object.date()

            if day not in daily_temps:
                daily_temps[day] = {'min_temp': float('inf'), 'max_temp': float('-inf'), 'descriptions': set()}
            
            daily_temps[day]['min_temp'] = min(daily_temps[day]['min_temp'], item['main']['temp_min'])
            daily_temps[day]['max_temp'] = max(daily_temps[day]['max_temp'], item['main']['temp_max'])
            daily_temps[day]['descriptions'].add(item['weather'][0]['description'].capitalize())

        sorted_days = sorted(daily_temps.keys())

        for i, daily_frame_data in enumerate(self.daily_frames):
            if i < len(sorted_days):
                day = sorted_days[i]
                forecast = daily_temps[day]
                day_name = day.strftime("%a, %b %d")
                descriptions_str = ", ".join(list(forecast['descriptions'])[:2])

                daily_frame_data['day'].config(text=day_name)
                daily_frame_data['temp_max'].config(text=f"Max: {forecast['max_temp']:.1f}°C")
                daily_frame_data['temp_min'].config(text=f"Min: {forecast['min_temp']:.1f}°C")
                daily_frame_data['desc'].config(text=descriptions_str)
            else:
                daily_frame_data['day'].config(text="N/A")
                daily_frame_data['temp_max'].config(text="N/A")
                daily_frame_data['temp_min'].config(text="N/A")
                daily_frame_data['desc'].config(text="N/A")

    def update_additional_info(self, data):
        cloudiness = f"{data['clouds']['all']}%"
        wind_gust = f"{data['wind'].get('gust', 'N/A')} m/s"

        sea_level = "N/A"
        if 'sea_level' in data['main']:
            sea_level = f"{data['main']['sea_level']} hPa"
        elif 'grnd_level' in data['main']:
            sea_level = f"{data['main']['grnd_level']} hPa (Grnd)"

        ground_level = "N/A"
        if 'grnd_level' in data['main']:
            ground_level = f"{data['main']['grnd_level']} hPa"

        coords = f"Lat: {data['coord']['lat']:.2f}, Lon: {data['coord']['lon']:.2f}"
        tz_offset = f"{data['timezone'] / 3600:.0f} hours"

        self.cloudiness_label.config(text=f"Cloudiness: {cloudiness}")
        self.gust_speed_label.config(text=f"Wind Gust: {wind_gust}")
        self.sea_level_label.config(text=f"Sea Level Pressure: {sea_level}")
        self.ground_level_label.config(text=f"Ground Level Pressure: {ground_level}")
        self.coordinates_label.config(text=f"Coordinates: {coords}")
        self.time_zone_label.config(text=f"Time Zone Offset: UTC{tz_offset}")

        self.info_placeholder_one.config(text="Extended Data Point 1: Active")
        self.info_placeholder_two.config(text="Extended Data Point 2: Operational")
        self.info_placeholder_three.config(text="Extended Data Point 3: Data Stream Nominal")
        self.info_placeholder_four.config(text="Extended Data Point 4: Forecast Model v2.1")

    def update_status(self, message):
        self.status_message.config(text=message)

    def update_last_updated(self):
        current_time_gmt = datetime.datetime.utcnow()
        self.last_updated_label.config(text=f"Last Updated: {current_time_gmt.strftime('%Y-%m-%d %H:%M:%S UTC')}")

    def update_clock(self):
        current_local_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.current_time_label.config(text=f"Local Time: {current_local_time}")
        self.master.after(1000, self.update_clock)

    def update_weather_periodically(self):
        if self.city_entry.get():
            self.fetch_weather_data()
        self.master.after(600000, self.update_weather_periodically)

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()