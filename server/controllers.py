import subprocess

def ssh_shutdown():
    #This will no longer work during dev mode due to requiring a valid key
    key_path = "../.ssh/pi_ssh"  
    user = "peasantl"
    host = "192.168.1.107"
    shutdown_command = "sudo shutdown now"
    
    ssh_command = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-i", key_path,
        f"{user}@{host}",
        shutdown_command
    ]

    result = subprocess.run(ssh_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.returncode, result.stdout, result.stderr


def WOL():
    host = "192.168.1.107"
    host_mac = "18:C0:4D:89:82:94"
    command = [
        "wakeonlan",
        "-i", host,
        host_mac
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.returncode, result.stdout, result.stderr


#For running script based on path
def run_script(script_string):
    key_path = "../.ssh/pi_ssh"  
    user = "peasantl"
    host = "192.168.1.107"    
    ssh_command = f"ssh -o StrictHostKeyChecking=no -i {key_path} -X {user}@{host} '{script_string}'"

    result = subprocess.run(ssh_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.returncode, result.stdout, result.stderr


def fetch_ping(script_path):
    process = subprocess.Popen(script_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    return process.returncode