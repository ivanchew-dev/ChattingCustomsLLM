
import os
import csv
from typing import List, Any

def find_file_in_parent_directories(filename, start_directory=None):
    """
    Recursively searches for a file in the given directory and its parent directories.

    Args:
        filename (str): The name of the file to search for.
        start_directory (str, optional): The directory to start the search from.
                                         If None, the current working directory is used.

    Returns:
        str or None: The full path to the file if found, otherwise None.
    """
    print(filename)
    if start_directory is None:
        current_dir = os.getcwd()
    else:
        current_dir = os.path.abspath(start_directory)

    while True:
        file_path = os.path.join(current_dir, filename)
        if os.path.exists(file_path) and os.path.isfile(file_path):
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
       
        script_directory = os.path.dirname(os.path.abspath(__file__))
        app_parent_directory_path= find_file_in_parent_directories(".env",script_directory)[:-4]
        
        print(app_parent_directory_path)
        datastore_path = app_parent_directory_path + "datastore/appData/"
        with open(datastore_path + file_name, 'a', newline='', encoding='utf-8') as file:

            # Create a csv.writer object
            writer = csv.writer(file,quoting=csv.QUOTE_STRINGS)

            # Write the data list as a new row
            writer.writerow(new_row)

        print(f"✅ Data successfully appended to or created: {file_name}")
        return True

    except Exception as e:
        print(f"❌ An error occurred while writing to {file_name}: {e}")
        return False