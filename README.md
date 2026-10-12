# Unified Time & Weather App

A desktop app built with Python and Tkinter that combines a world clock, analog clocks, city suggestions, and live weather forecasts in a single window. The interface switches automatically between light and dark mode depending on whether it's day or night in your selected time zone.

## Features

- **Main digital clock** with a time-of-day greeting (Good Morning / Afternoon / Evening / Night) and full date
- **Selectable time zone** for the main clock (Mumbai, Bengaluru, New York, London, Tokyo, Sydney)
- **Automatic dark/light theme**: dark between 6 PM and 6 AM in the selected time zone, light otherwise
- **World clocks panel** showing the current time, a greeting, and a local attraction suggestion for each city
- **Add your own city**: enter a name and pick any time zone; a default attraction suggestion is generated automatically
- **Weather & 3-day forecast** for any city, powered by OpenWeatherMap
- **Analog clocks** for Mumbai, New York, London, and Tokyo, with hour, minute, and second hands

## Requirements

- Python 3.8 or later
- Tkinter (bundled with most Python installers; on some Linux distros install it separately, e.g. `sudo apt install python3-tk`)
- Python packages:
  - `pytz`
  - `requests`
- A free [OpenWeatherMap API key](https://openweathermap.org/api)
- Internet connection (for weather data only; clocks work offline)

## Quick Start

1. **Clone or download** the project and open a terminal in its folder.

2. **Install dependencies:**

   ```bash
   pip install pytz requests
   ```

3. **Add your API key.** Open `unified_time_weather_final.py` and set your own key:

   ```python
   API_KEY = "your_openweathermap_api_key"
   ```

4. **Run the app:**

   ```bash
   python unified_time_weather_final.py
   ```

## Usage

| Task | How |
|------|-----|
| Change the main clock's time zone | Use the **Main Clock Time Zone** dropdown on the left |
| Add a city to the world clocks | Type a name under **Add Place**, choose a time zone in **TZ** (e.g. `Europe/Paris`), then click **Add** |
| Check the weather | Type a city in the weather box on the right and click **Fetch** |

World clocks refresh every 5 seconds; the main and analog clocks refresh every second.

## Configuration

All configuration lives at the top of `unified_time_weather_final.py`:

| Variable | Purpose |
|----------|---------|
| `API_KEY` | Your OpenWeatherMap API key |
| `CITY_TIMEZONES` | Cities shown in the world clocks panel at startup |
| `PLACE_RECOMMENDATIONS` | Attraction suggestion shown for each city |
| `AVAILABLE_ZONES` | Options in the main clock's time zone dropdown |

To add a permanent city, add an entry to `CITY_TIMEZONES` (city name to an [IANA time zone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)) and, optionally, a tip in `PLACE_RECOMMENDATIONS`.

## Project Structure

```
unified_time_weather_final.py   # Entire application (single file)
README.md
```

## How It Works

- **Clocks:** `pytz` converts the current time into each selected time zone. Tkinter's `after()` schedules the periodic refreshes.
- **Weather:** The app calls the OpenWeatherMap *Current Weather* and *5-day Forecast* endpoints, then samples one entry per day for a 3-day outlook. Requests run on a background thread so the window stays responsive.
- **Theming:** Each tick checks the hour in the selected time zone and recolors all widgets recursively when the day/night state changes.

## Troubleshooting

- **"Error fetching weather."** Check your internet connection, confirm the API key is valid (new keys can take a couple of hours to activate), and check the city spelling.
- **"Invalid Timezone" when adding a city.** Use the exact IANA name from the dropdown, such as `Asia/Dubai` or `Europe/Paris`.
- **`ModuleNotFoundError`.** Run `pip install pytz requests`.
- **`No module named tkinter`.** Install Tkinter for your OS (see Requirements).

## Security Note

Don't commit your API key to a public repository. For anything you share, load it from an environment variable instead:

```python
import os
API_KEY = os.environ.get("OWM_API_KEY", "")
```

Then run with `OWM_API_KEY=your_key python unified_time_weather_final.py` (macOS/Linux) or set the variable in your environment on Windows.

## Known Limitations

- City names added at runtime are not saved between sessions.
- The weather forecast shows one reading per day (roughly every 24 hours), not a daily average.
- The forecast dates use your computer's local time zone, not the searched city's.

## Possible Improvements

- Persist custom cities to a JSON file
- Add °C/°F toggle
- Let users manually override dark/light mode
- Weather icons and hourly forecast

## License

Add a license of your choice (e.g. MIT) here.
