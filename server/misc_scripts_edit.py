import os
import argparse
import pprint
from file_io import read_json, write_json

JSON_PATH = './misc_scripts.json'

def arguments():
    parser = argparse.ArgumentParser(description="Manage scripts.")

    parser.add_argument("-a", metavar="SCRIPT_PATH",
                        help="Adds a script, requries the path to the script")
    parser.add_argument("-d", metavar="SCRIPT_NAME",
                        help="Deletes a script, requires the name of the script")
    return parser.parse_args()

# Main script logic
def main(args):
    data = read_json(JSON_PATH) if os.path.isfile(JSON_PATH) else {}

    #Adding script
    if args.a:
        script_path = args.a

        if script_path.startswith('file://'):
            script_path = script_path[len('file://'):]
        else:
            script_path = script_path

        if not script_path.endswith('.sh'):
            raise Exception('Error: only shell scripts are currently accepted')
        if not os.path.isfile(script_path):
            raise Exception('Error: file does not exist')
        
        script_name = os.path.basename(script_path)
        data[script_name] = script_path 
        write_json(JSON_PATH, data)
        print(f"Added script: {script_name}")
    
    #Deleting script
    elif args.d:  
        script_name = args.d
        if script_name in data:
            del data[script_name]
            write_json(JSON_PATH, data)
            print(f"Deleted script: {script_name}")
        else:
            print("Script not found.")

    #Default print data
    else:  
        print("\nScripts data:\n")
        for name, path in data.items():
            pprint.pprint(f"{name}: {path}")

if __name__ == "__main__":
    try:
        args = arguments()
        main(args)
    except Exception as e:
        print(f'An error occurred: {e}')
