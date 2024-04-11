import subprocess
import toml

# Load config from TOML file
config = toml.load('config.toml')

# Use the config variables
key_path = config['key_paths']['ssh_key']
user = config['network']['user']
host = config['network']['host']
host_mac = config['network']['host_mac']

def ssh_shutdown():
    ssh_command = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-i", key_path,
        f"{user}@{host}",
        "sudo shutdown now"
    ]

    result = subprocess.run(ssh_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.returncode, result.stdout, result.stderr


def WOL():
    command = [
        "wakeonlan",
        "-i", host,
        host_mac
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.returncode, result.stdout, result.stderr


def run_script(script_string):
    ssh_command = f"ssh -o StrictHostKeyChecking=no -i {key_path} -X {user}@{host} '{script_string}'"

    result = subprocess.run(ssh_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.returncode, result.stdout, result.stderr


def fetch_ping(script_path):
    command = f"{script_path} {host}"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    return process.returncode