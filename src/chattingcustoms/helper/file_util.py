
import os
import csv
from typing import List, Any


def find_file_in_parent_directories(filename: str, start_directory: str = None) -> str:
    """
    Searches for a file in the current directory and parent directories.
    
    Args:
        filename (str): The name of the file to search for.
        start_directory (str, optional): Directory to start searching from. 
                                       If None, uses current working directory.
    
    Returns:
        str: Absolute path to the file if found, None otherwise.
    """
    if start_directory is None:
        start_directory = os.getcwd()
    
    current_dir = os.path.abspath(start_directory)
    
    while True:
        file_path = os.path.join(current_dir, filename)
        if os.path.isfile(file_path):
            return file_path
        
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # Reached the root directory
            return None
        current_dir = parent_dir


def append_to_csv(file_name: str, new_row: List[Any]) -> bool:
    """
    Appends a single row of data to a CSV file.
    If the file does not exist, it will be created.

    Args:
        file_name (str): The name of the CSV file.
        new_row (List[Any]): A list containing the data for the new row.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    try:
        # Open the file in append mode ('a'). 
        # If the file does not exist, it will be created.
        # newline='' prevents blank rows from being inserted.
       
        # Get the root directory path relative to this script location
        # This script is in src/chattingcustoms/helper/, so go up 3 levels to reach project root
        script_directory = os.path.dirname(os.path.abspath(__file__))
        root_directory = os.path.join(script_directory, "..", "..", "..")
        
        print(f"Root directory: {os.path.abspath(root_directory)}")
        datastore_path = os.path.join(root_directory, "datastore", "appData")
        full_file_path = os.path.join(datastore_path, file_name)
        
        with open(full_file_path, 'a', newline='', encoding='utf-8') as file:

            # Create a csv.writer object
            writer = csv.writer(file,quoting=csv.QUOTE_STRINGS)

            # Write the data list as a new row
            writer.writerow(new_row)

        print(f"✅ Data successfully appended to or created: {file_name}")
        return True

    except Exception as e:
        print(f"❌ An error occurred while writing to {file_name}: {e}")
        return False