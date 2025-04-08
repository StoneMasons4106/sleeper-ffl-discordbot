import discord
import os
import requests
import functions

if os.path.exists("env.py"):
    import env


def forecast(bot, city: str):
    weather_api_key = os.environ.get("WEATHER_API_KEY")
    forecast = requests.get(
        "http://api.weatherapi.com/v1/forecast.json",
        params={"key": weather_api_key, "q": city, "days": 3},
    )
    if forecast.status_code == 200:
        forecast_string = ""
        tuple_test = type(city) is tuple
        if tuple_test:
            city_string = ""
            for word in city:
                city_string += f"{word} "
            city = city_string
        else:
            pass
        for day in forecast.json()["forecast"]["forecastday"]:
            forecast_string += f'{day["date"]}:\nHigh: {day["day"]["maxtemp_f"]} degrees F\nLow: {day["day"]["mintemp_f"]} degrees F\nWind: {day["day"]["maxwind_mph"]} mph\nPrecipitation Amount: {day["day"]["totalprecip_in"]} in.\nHumidity: {day["day"]["avghumidity"]}%\nChance of Rain: {day["day"]["daily_chance_of_rain"]}%\nChance of Snow: {day["day"]["daily_chance_of_snow"]}%\nGeneral Conditions: {day["day"]["condition"]["text"]}\n\n'
        embed = functions.my_embed(
            "Weather Forecast",
            f'3 day forecast for {forecast.json()["location"]["name"]}, {forecast.json()["location"]["region"]}',
            discord.Colour.blue(),
            f"Forecast for {city}",
            forecast_string,
            False,
            bot,
        )
    else:
        embed = "Invalid city name or zip code, please try again!"
    return embed


def current_weather(bot, city: str):
    weather_api_key = os.environ.get("WEATHER_API_KEY")
    current_weather = requests.get(
        "http://api.weatherapi.com/v1/current.json",
        params={"key": weather_api_key, "q": city},
    )
    if current_weather.status_code == 200:
        tuple_test = type(city) is tuple
        if tuple_test:
            city_string = ""
            for word in city:
                city_string += f"{word} "
            city = city_string
        else:
            pass
        current_weather_string = f'Local Time: {current_weather.json()["location"]["localtime"]}\nTemperature: {current_weather.json()["current"]["temp_f"]} degrees F\nFeels like: {current_weather.json()["current"]["feelslike_f"]} degrees F\nCurrent condition: {current_weather.json()["current"]["condition"]["text"]}\nWind: {current_weather.json()["current"]["wind_mph"]} mph\nWind Direction: {current_weather.json()["current"]["wind_dir"]}\nGust Speed: {current_weather.json()["current"]["gust_mph"]} mph\nHumidity: {current_weather.json()["current"]["humidity"]}%\n'
        embed = functions.my_embed(
            "Current Weather",
            f'Current weather for {current_weather.json()["location"]["name"]}, {current_weather.json()["location"]["region"]}',
            discord.Colour.blue(),
            f"Current Weather for {city}",
            current_weather_string,
            False,
            bot,
        )
    else:
        embed = "Invalid city name or zip code, please try again!"
    return embed
