import subprocess
import base64
import json

def run_oc_command(command, capture_output=True):
    try:
        result = subprocess.run(
            command, shell=True, check=True, text=True, capture_output=capture_output
        )
        return result.stdout.strip() if capture_output else None
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}\n{e.stderr}")
        return None

def login_to_cluster(cluster_url, username, password):
    print(f"Logging into cluster: {cluster_url}")
    command = f"oc login {cluster_url} -u {username} -p {password} --insecure-skip-tls-verify"
    result = run_oc_command(command)
    if result:
        print("Login successful")
    else:
        print("Login failed")
    return result

def get_projects():
    print("Fetching project list...")
    command = "oc get projects -o json"
    result = run_oc_command(command)
    if result:
        projects = json.loads(result).get("items", [])
        return [project["metadata"]["name"] for project in projects]
    else:
        print("Failed to get projects")
        return []

def check_secrets(project):
    print(f"Checking secrets in namespace: {project}")
    command = f"oc get secrets -n {project} -o json"
    result = run_oc_command(command)
    secret_values = {}
    if result:
        secrets = json.loads(result).get("items", [])
        for secret in secrets:
            name = secret["metadata"]["name"]
            if name in ["registry-nonprod", "registry-prod"]:
                secret_data = secret.get("data", {})
                decoded_data = {
                    key: base64.b64decode(value).decode('utf-8')
                    for key, value in secret_data.items()
                }
                secret_values[name] = decoded_data
    return secret_values

def main():
    clusters = [
        "https://openshift-cluster1.example.com:6443",
        "https://openshift-cluster2.example.com:6443"
    ]
    username = "your-username"
    password = "your-password"

    for cluster in clusters:
        if login_to_cluster(cluster, username, password):
            projects = get_projects()
            for project in projects:
                secrets = check_secrets(project)
                if secrets:
                    print(f"Namespace: {project}, Secrets: {secrets}")
                else:
                    print(f"No matching secrets found in namespace: {project}")

if __name__ == "__main__":
    main()
