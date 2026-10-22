"""Live Weather Report — Open-Meteo (keyless) + wttr.in + browser fallback."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
import webbrowser

_WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Rain showers", 81: "Moderate showers", 82: "Violent showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Severe thunderstorm",
}


def _http_json(url: str, timeout: float = 6.0) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "MarkLV-OS/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def _fetch_open_meteo(city: str, units: str = "metric") -> str | None:
    geo_url = (
        "https://geocoding-api.open-meteo.com/v1/search?count=1&language=en&name="
        + urllib.parse.quote_plus(city)
    )
    geo = _http_json(geo_url)
    results = geo.get("results") or []
    if not results:
        return None

    loc = results[0]
    lat, lon = loc["latitude"], loc["longitude"]
    label = ", ".join(p for p in (loc.get("name"), loc.get("country")) if p)
    temp_unit = "fahrenheit" if units == "imperial" else "celsius"
    wind_unit = "mph" if units == "imperial" else "kmh"
    t_sym = "°F" if units == "imperial" else "°C"

    wx_url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,apparent_temperature,relative_humidity_2m,"
        f"weather_code,wind_speed_10m"
        f"&daily=weather_code,temperature_2m_max,temperature_2m_min"
        f"&forecast_days=3&timezone=auto"
        f"&temperature_unit={temp_unit}&wind_speed_unit={wind_unit}"
    )
    wx = _http_json(wx_url)
    cur = wx.get("current") or {}
    daily = wx.get("daily") or {}

    cond = _WMO_CODES.get(int(cur.get("weather_code", -1)), "Variable conditions")
    temp = cur.get("temperature_2m", "?")
    feels = cur.get("apparent_temperature", "?")
    hum = cur.get("relative_humidity_2m", "?")
    wind = cur.get("wind_speed_10m", "?")

    lines = [
        f"Weather for {label}: {cond}, {temp}{t_sym} (feels like {feels}{t_sym})",
        f"Humidity: {hum}% | Wind: {wind} {wind_unit}",
    ]
    dates = daily.get("time") or []
    highs = daily.get("temperature_2m_max") or []
    lows = daily.get("temperature_2m_min") or []
    codes = daily.get("weather_code") or []
    if dates and highs and lows:
        lines.append("3-day outlook:")
        for d, hi, lo, cd in zip(dates[:3], highs[:3], lows[:3], codes[:3]):
            desc = _WMO_CODES.get(int(cd), "")
            lines.append(f"  • {d}: {lo}{t_sym} – {hi}{t_sym} ({desc})")
    return "\n".join(lines)


def weather_action(
    parameters: dict,
    player=None,
    session_memory=None,
    **_,
) -> str:
    city = (parameters or {}).get("city")
    when = str((parameters or {}).get("time") or "today").strip()
    units = str((parameters or {}).get("units") or "metric").strip().lower()

    if not city or not isinstance(city, str) or not city.strip():
        msg = "City is required for weather_report (check memory for user's city first)."
        _log(msg, player)
        return msg

    city = city.strip()

    # 1. Keyless live forecast via Open-Meteo
    try:
        report = _fetch_open_meteo(city, units=units)
        if report:
            if player and hasattr(player, "show_content"):
                player.show_content(f"WEATHER — {city.upper()}", report)
            _log(report.splitlines()[0], player)
            return report
    except Exception:
        pass

    # 2. Browser fallback if offline / geocoding blocked
    search_query = f"weather in {city} {when}"
    url = f"https://www.google.com/search?q={urllib.parse.quote_plus(search_query)}"
    try:
        opened = webbrowser.open(url)
        if not opened:
            raise RuntimeError("webbrowser.open returned False")
        msg = f"Live weather API unreachable; opened browser forecast for {city} ({when})."
    except Exception as e:
        msg = f"Could not fetch live weather for {city}: {e}"

    _log(msg, player)
    if session_memory:
        try:
            session_memory.set_last_search(query=search_query, response=msg)
        except Exception:
            pass
    return msg


def _log(message: str, player=None) -> None:
    print(f"[Weather] {message}")
    if player and hasattr(player, "write_log"):
        try:
            player.write_log(f"[Weather] {message}")
        except Exception:
            pass


TOOL = {
    "name": "weather_report",
    "description": (
        "Fetch live weather (temperature, feels-like, humidity, wind, and "
        "3-day high/low outlook) for a city via Open-Meteo — no API key "
        "required. Falls back to opening a browser forecast if offline."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "city": {
                "type": "STRING",
                "description": "City name (e.g. 'Riyadh', 'London', 'Tokyo')",
            },
            "time": {
                "type": "STRING",
                "description": "Optional timeframe hint (e.g. 'today', 'tomorrow')",
            },
            "units": {
                "type": "STRING",
                "description": "metric (default, °C) or imperial (°F)",
            },
        },
        "required": ["city"],
    },
    "handler": weather_action,
}
