import requests

def get_address(api_key, latitude, longitude):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "latlng": f"{latitude},{longitude}",
        "key": api_key,
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if data["status"] == "OK" and data["results"]:
        # Extract the formatted address from the first result
        return data["results"][0]["formatted_address"]
    else:
        return None

# Replace 'your_api_key' with your actual Google Maps API key
api_key = 'your_api_key'
latitude = 37.7749  # Replace with your actual latitude
longitude = -122.4194  # Replace with your actual longitude

address = get_address(api_key, latitude, longitude)
if address:
    print(f"The address is: {address}")
else:
    print("Failed to retrieve the address.")
