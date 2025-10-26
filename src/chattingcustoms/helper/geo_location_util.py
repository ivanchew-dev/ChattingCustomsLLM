import os
import geoip2.database

def get_location_from_ip_local(ip_address):
    """
    Retrieves latitude and longitude from an IP address using a local MaxMind database.

    Args:
        ip_address (str): The IP address to look up.
        db_path (str): The path to the GeoLite2-City.mmdb file.

    Returns:
        tuple: (latitude, longitude) or None if location is not found.
    """
    try:
        # Get the root directory path relative to this script location
        # This script is in src/chattingcustoms/helper/, so go up 3 levels to reach project root
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.join(script_dir, "..", "..", "..")
        db_path = os.path.join(root_dir, "datastore", "ragData", "GeoLite2-City.mmdb")
        # Create a reader object, specifying the path to your downloaded .mmdb file
        with geoip2.database.Reader(db_path) as reader:
            response = reader.city(ip_address)
            
            latitude = response.location.latitude
            longitude = response.location.longitude
            city = response.city.name
            country = response.country.name
            
            print(f"IP: {ip_address}")
            print(f"Location: {city}, {country}")
            
            return (latitude, longitude)

    except FileNotFoundError:
        print(f"Error: MaxMind database file not found at '{db_path}'.")
        print("Please download GeoLite2-City.mmdb and ensure the path is correct.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
