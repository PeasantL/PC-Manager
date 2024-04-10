import json

# Function to read the JSON file
def read_json(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise Exception(f'Error reading JSON file: {e}')
    except Exception as e:
        raise Exception(f'An unexpected error occurred: {e}')

# Function to write to the JSON file
def write_json(file_path, data):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file)
    except FileNotFoundError:
        raise Exception('Error: JSON file not found.')
    except json.JSONDecodeError:
        raise Exception('Error: failed to process JSON data.')
    except Exception as e:
        raise Exception(f'An error occurred: {str(e)}')
