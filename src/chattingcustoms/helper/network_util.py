import requests
from typing import Optional

def get_public_ip() -> Optional[str]:
    """
    Retrieves the public IP address of the client machine by querying an 
    external IP address API service.

    Returns:
        Optional[str]: The public IP address as a string, or None if the 
                       request fails due to an error.
    """
    # A reliable, free, and lightweight service to check external IP
    api_url = "https://api.ipify.org"
    
    # We use a timeout to prevent the script from hanging indefinitely 
    # if the network connection is slow or the server is unresponsive.
    TIMEOUT_SECONDS = 5

    try:
        # Send a GET request to the API
        response = requests.get(api_url, timeout=TIMEOUT_SECONDS)
        
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status() 

        # The API returns the IP address as plain text in the response body
        public_ip = response.text.strip()
        
        return public_ip

    except requests.exceptions.RequestException as e:
        # This catches connection errors, DNS errors, timeouts, and bad HTTP statuses
        print(f"❌ Error retrieving public IP: {e}")
        # Return None to signify failure
        return None
    except Exception as e:
        # Catch any other unexpected errors
        print(f"❌ An unexpected error occurred: {e}")
        return None