import geoip2.database
from helper import file_util

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
        
        app_parent_directory_path= file_util.find_file_in_parent_directories(".env")[:-4]
        db_path = app_parent_directory_path + "datastore/ragData/GeoLite2-City.mmdb"
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
