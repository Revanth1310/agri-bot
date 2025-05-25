import streamlit as st
import streamlit.components.v1 as components
import requests

OPENWEATHER_API_KEY = "f5efed3913e16c7855b9a6423d17cd90"  # Replace with your actual key

def get_coords_from_browser():
    try:
        response = requests.get("http://ip-api.com/json/")
        data = response.json()
        lat = data.get("lat")
        lon = data.get("lon")
        if lat is None or lon is None:
            print("Could not get location from IP.")
            return None, None
        return lat, lon
    except Exception as e:
        print(f"Error fetching IP location: {e}")
        return None, None


def get_environment_data(lat, lon):
    try:
        weather_url = (
            f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}"
            f"&appid={OPENWEATHER_API_KEY}&units=metric"
        )
        weather_data = requests.get(weather_url).json()
        temp = weather_data["main"]["temp"]
        t = round(temp, 1)

        soil_url = (
            f"https://rest.isric.org/soilgrids/v2.0/properties/query"
            f"?lat={lat}&lon={lon}&property=ocd&depth=0-5cm"
        )
        soil_data = requests.get(soil_url).json()

        if 'ocd' in soil_data.get('properties', {}):
            layers = soil_data['properties']['ocd']['layers']
            if layers and 'values' in layers[0] and 'mean' in layers[0]['values']:
                m = round(layers[0]['values']['mean'], 1)
            else:
                m = "N/A"
        else:
            m = "N/A"

        air_quality = "Moderate"  # Still mock
        return {
            "temperature": t,
            "soil_moisture": m,
            "air_quality": air_quality
        }
    except Exception as e:
        print("ERROR IN get_environment_data():", e)
        return {
            "temperature": "N/A",
            "soil_moisture": "N/A",
            "air_quality": "N/A"
        }
