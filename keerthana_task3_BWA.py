import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

import requests

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
IP_INFO_URL = "https://ipinfo.io/json"


def build_query(location):
    cleaned = (location or "").strip()
    if not cleaned:
        raise ValueError("Please enter a city name or ZIP code.")

    numeric_value = cleaned.replace(",", "").replace(" ", "")
    if numeric_value.isdigit():
        return {"zip": cleaned}
    return {"q": cleaned}


def weather_icon(condition):
    icons = {
        "Clear": "☀️",
        "Clouds": "☁️",
        "Rain": "🌧️",
        "Drizzle": "🌦️",
        "Thunderstorm": "⛈️",
        "Snow": "❄️",
        "Mist": "🌫️",
        "Fog": "🌫️",
        "Haze": "🌫️",
        "Smoke": "🌫️",
        "Dust": "🌫️",
        "Sand": "🌫️",
        "Ash": "🌫️",
        "Squall": "🌬️",
        "Tornado": "🌪️",
    }
    return icons.get(condition, "🌤️")


def format_temperature(value, units):
    if value is None:
        return "--"
    unit = "°C" if units == "metric" else "°F"
    return f"{value:.0f}{unit}"


def get_api_key():
    return (os.getenv("OPENWEATHER_API_KEY") or "").strip()


def fetch_json(url, params):
    try:
        response = requests.get(url, params=params, timeout=10)
    except requests.exceptions.Timeout:
        raise ValueError("Network timeout. Please try again.") from None
    except requests.exceptions.RequestException as exc:
        raise ValueError(f"Network error: {exc}") from exc

    if response.status_code == 401:
        raise ValueError("Invalid API key. Please enter a valid OpenWeatherMap API key.")
    if response.status_code == 404:
        raise ValueError("City or ZIP code not found. Please check your input.")
    if response.status_code >= 400:
        raise ValueError(f"Weather service error: {response.status_code}")

    try:
        data = response.json()
    except ValueError as exc:
        raise ValueError("The weather service returned an invalid response.") from exc

    return data


def fetch_weather_data(location, api_key, units):
    if not api_key:
        raise ValueError(
            "OpenWeatherMap API key is missing. Enter it in the field or set OPENWEATHER_API_KEY."
        )

    lookup = build_query(location)
    query_params = {
        "appid": api_key,
        "units": units,
        **lookup,
    }

    current = fetch_json(WEATHER_URL, query_params)
    forecast = fetch_json(FORECAST_URL, {**query_params, "cnt": 40})
    return current, forecast


def fetch_ip_location():
    try:
        response = requests.get(IP_INFO_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as exc:
        raise ValueError("Could not detect your location automatically.") from exc

    if not isinstance(data, dict):
        raise ValueError("Could not detect your location automatically.")

    city = data.get("city")
    region = data.get("region")
    if city:
        return f"{city}, {region}" if region else city
    if "loc" in data:
        return data["loc"]
    raise ValueError("Location data is unavailable for your IP address.")


def extract_hourly_forecast(forecast_data, limit=6):
    items = forecast_data.get("list", [])[:limit]
    rows = []
    for item in items:
        time = datetime.fromtimestamp(item["dt"]).strftime("%H:%M")
        main = item.get("main", {})
        weather = item.get("weather", [{}])[0]
        condition = weather.get("main", "Weather")
        temp = main.get("temp")
        rows.append((time, condition, temp))
    return rows


def extract_daily_forecast(forecast_data, limit=5):
    grouped = {}
    entries = forecast_data.get("list", [])

    for item in entries:
        date_key = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
        if date_key not in grouped:
            grouped[date_key] = item
        else:
            current_hour = datetime.fromtimestamp(item["dt"]).hour
            if current_hour in (12, 13, 14):
                grouped[date_key] = item

    ordered = [grouped[key] for key in sorted(grouped)[:limit]]
    rows = []
    for item in ordered:
        stamp = datetime.fromtimestamp(item["dt"])
        main = item.get("main", {})
        weather = item.get("weather", [{}])[0]
        rows.append((stamp.strftime("%a"), weather.get("main", "Weather"), main.get("temp_min"), main.get("temp_max")))
    return rows


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App")
        self.root.geometry("430x330")
        self.root.configure(bg="#2b2d31")
        self.root.resizable(False, False)

        self.units = "metric"
        self.last_query = "Vadodara"

        self.card = tk.Frame(root, bg="#f2f2f2", highlightbackground="#000000", highlightthickness=1)
        self.card.pack(expand=True, padx=20, pady=22)

        tk.Label(self.card, text="Weather App", bg="#f2f2f2", fg="#1d1d1d", font=("Arial", 22, "bold")).pack(pady=(18, 12))

        self.city_var = tk.StringVar(value="Hyderabad")
        self.city_options = [
            "Hyderabad",
            "Vadodara",
            "Delhi",
            "Mumbai",
            "Chennai",
            "London",
            "New York",
            "Tokyo",
            "Amsterdam",
            "Athens",
            "Austin",
            "Auckland",
            "Abu Dhabi",
            "Accra",
            "Algiers",
            "Ankara",
            "Baghdad",
            "Bangkok",
            "Bengaluru",
            "Beijing",
            "Berlin",
            "Cairo",
            "Cape Town",
            "Chicago",
            "Dubai",
            "Frankfurt",
            "Goa",
            "Hong Kong",
            "Jakarta",
            "Johannesburg",
            "Kolkata",
            "Los Angeles",
            "Mexico City",
            "Moscow",
            "Paris",
            "Rome",
            "Seoul",
            "Singapore",
            "Sydney",
            "Toronto",
            "Zurich",
        ]
        self.city_entry = ttk.Combobox(
            self.card,
            textvariable=self.city_var,
            values=self.city_options,
            width=24,
            font=("Arial", 12),
            state="normal",
        )
        self.city_entry.pack(pady=(0, 10))
        self.city_entry.bind("<<ComboboxSelected>>", lambda event: self.set_demo_weather(self.city_var.get()))
        self.city_entry.bind("<KeyRelease>", self.filter_city_suggestions)

        self.get_weather_btn = ttk.Button(self.card, text="Get Weather", command=self.get_weather)
        self.get_weather_btn.pack(pady=(0, 12))

        self.result = tk.Label(
            self.card,
            text="",
            justify="left",
            bg="#f2f2f2",
            fg="#111111",
            font=("Arial", 11),
            anchor="w",
            padx=18,
            pady=8,
        )
        self.result.pack(fill="x")

        self.root.bind("<Return>", lambda event: self.get_weather())
        self.set_demo_weather()

    def filter_city_suggestions(self, event=None):
        if event and event.keysym in {"Down", "Up", "Return", "Escape", "Tab"}:
            return

        typed = self.city_var.get().strip().lower()
        if not typed:
            self.city_entry.configure(values=self.city_options)
            return

        matching = [city for city in self.city_options if city.lower().startswith(typed)]
        if matching:
            self.city_entry.configure(values=matching)
        else:
            self.city_entry.configure(values=[typed.title()])
        self.city_entry.tk.call("ttk::combobox::Post", self.city_entry)

    def set_demo_weather(self, city=None):
        location = city or self.city_var.get() or "Vadodara"
        demo_data = {
            "Hyderabad": {"temp": 31.20, "humidity": 46, "condition": "Clear Sky", "wind": 3.50, "pressure": 1011, "country": "IN"},
            "Vadodara": {"temp": 30.99, "humidity": 25, "condition": "Clear Sky", "wind": 3.09, "pressure": 1012, "country": "IN"},
            "Delhi": {"temp": 34.12, "humidity": 41, "condition": "Sunny", "wind": 4.20, "pressure": 1009, "country": "IN"},
            "Mumbai": {"temp": 29.40, "humidity": 78, "condition": "Cloudy", "wind": 5.10, "pressure": 1010, "country": "IN"},
            "Chennai": {"temp": 32.80, "humidity": 68, "condition": "Humid", "wind": 3.80, "pressure": 1008, "country": "IN"},
            "London": {"temp": 18.50, "humidity": 65, "condition": "Mist", "wind": 7.20, "pressure": 1015, "country": "GB"},
            "New York": {"temp": 22.30, "humidity": 52, "condition": "Partly Cloudy", "wind": 6.50, "pressure": 1017, "country": "US"},
            "Tokyo": {"temp": 26.70, "humidity": 58, "condition": "Rainy", "wind": 4.90, "pressure": 1006, "country": "JP"},
        }
        data = demo_data.get(location, demo_data["Vadodara"])
        self.result.config(
            text=(
                f"City: {location}, {data['country']}\n"
                f"Temperature: {data['temp']:.2f} °C / {(data['temp'] * 9 / 5) + 32:.2f} °F\n"
                f"Humidity: {data['humidity']}%\n"
                f"Weather Condition: {data['condition']}\n"
                f"Wind Speed: {data['wind']:.2f} m/s\n"
                f"Pressure: {data['pressure']} hPa"
            )
        )

    def show_error(self, message):
        self.result.config(text=f"Error: {message}")
        messagebox.showerror("Weather Error", message)

    def update_current_display(self, data):
        city = data.get("name", "Unknown City")
        country = data.get("sys", {}).get("country", "")
        main = data.get("main", {})
        weather = data.get("weather", [{}])[0]
        wind = data.get("wind", {})

        temp = main.get("temp")
        humidity = main.get("humidity")
        pressure = main.get("pressure")
        condition = weather.get("description", "Weather").title()
        wind_speed = wind.get("speed")

        celsius = temp if self.units == "metric" else (temp * 9 / 5) + 32
        formatted = (
            f"City: {city}, {country}\n"
            f"Temperature: {temp:.2f} °C / {celsius:.2f} °F\n"
            f"Humidity: {humidity}%\n"
            f"Weather Condition: {condition}\n"
            f"Wind Speed: {wind_speed} m/s\n"
            f"Pressure: {pressure} hPa"
        )
        self.result.config(text=formatted)

    def get_weather(self):
        api_key = get_api_key()
        location = self.city_var.get().strip() or self.last_query
        self.last_query = location

        if not api_key:
            self.set_demo_weather()
            return

        try:
            data, _ = fetch_weather_data(location, api_key, self.units)
        except ValueError as exc:
            self.show_error(str(exc))
            return

        self.update_current_display(data)


def main():
    try:
        root = tk.Tk()
        app = WeatherApp(root)
        root.mainloop()
    except tk.TclError as exc:
        print(f"Tkinter could not start: {exc}")


if __name__ == "__main__":
    main()
