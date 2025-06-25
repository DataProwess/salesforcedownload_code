import csv
import os
import requests
from datetime import datetime
import re
from dotenv import load_dotenv
import argparse

load_dotenv()

def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name)

# ==== CONFIGURATION ====
# CSV_FILE = "report1746679951782in.csv"  # Path to your CSV

SF_CLIENT_ID = os.getenv("SF_CLIENT_ID")
SF_CLIENT_SECRET = os.getenv("SF_CLIENT_SECRET")
SF_USERNAME = os.getenv("SF_USERNAME")
SF_PASSWORD = os.getenv("SF_PASSWORD")
SF_SECURITY_TOKEN = os.getenv("SF_SECURITY_TOKEN")  # Optional, only if needed

# ==== STEP 1: Authenticate to Salesforce ====
# auth_url = "https://lendlease--uat.sandbox.my.salesforce.com/services/oauth2/token"
# auth_url = "https://lendlease.my.salesforce.com/services/oauth2/token"
# auth_url = "https://lendlease.my.salesforce.com/app/mgmt/forceconnectedapps/forceAppDetail.apexp?applicationId=06POZ0000000JAj&applicationId=06POZ0000000JAj&id=0CiOZ00000004Wf"

# auth_payload = {
#     "grant_type": "password",
#     "client_id": SF_CLIENT_ID,
#     "client_secret": SF_CLIENT_SECRET,
#     "username": SF_USERNAME, 
#     "password": SF_PASSWORD + SF_SECURITY_TOKEN 
# }

# auth_response = requests.post(auth_url, data=auth_payload).json()
# print(f" Auth response: {auth_response}")

# if "access_token" not in auth_response:
#     raise Exception(f"Auth failed: {auth_response}")

access_token =  "00D28000001yqXX!AQ8AQEvZS4vxUjJbGlFYq8Xh_wba0jtS2KhbmH61Ni8J552DAvfSQq7WRPznl9_F7FLKtnSkxaQ_7um5vkZ0V_u9U2OFNjW." #auth_response["access_token"]
instance_url ="https://lendlease-as.my.salesforce.com" #auth_response["instance_url"]
headers = {"Authorization": f"Bearer {access_token}"}


###########
# Authenticate to Salesforce
# TOKEN_URL="https://login.salesforce.com/services/oauth2/authorize?redirect_uri=https://login.salesforce.com/services/oauth2/success&response_type=code" 
# payload = {
#             # "grant_type": "password",
#             "response_type": "code",
#             "client_id": SF_CLIENT_ID,
#             # "client_secret": SF_CLIENT_SECRET,
#             # "username": SF_USERNAME, 
#             # "password": SF_PASSWORD + SF_SECURITY_TOKEN 
#         }
# headers = {'Content-Type': 'application/x-www-form-urlencoded'}
# response = requests.post(TOKEN_URL, data=payload, headers=headers)
# print(response.status_code)
# print(response.content)
# print(response.text)

# ==== STEP 2: Use a specific project name ====
# ==== Argument Parsing ====
parser = argparse.ArgumentParser(description='Download Salesforce documents for a project.')
parser.add_argument('project_name', help='Name of the project to process.')
args = parser.parse_args()

project_name = args.project_name
sanitized_projectname=sanitize_filename(project_name)  # Sanitize project name for file system compatibility
print(f"📝 Using specific project: {project_name}")

# ==== STEP 3: Prepare Timestamped Download Folder ====
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
base_dir = os.getcwd()  # Gets current working directory on Windows or any OS
base_download_dir = os.path.join(base_dir, "salesforce_document_folder_downloads", f"SalesForceProjectsDownload_{sanitized_projectname}_{timestamp}")
os.makedirs(base_download_dir, exist_ok=True)
total_files_downloaded = 0
total_folders_created = set()

# ==== STEP 4: Loop through Projects and Download Files ====

print(f"\n📁 Project: {project_name}  ")

# Get Gates for this Project
gate_query = f"SELECT Id, Name FROM LLCompass_Gate__c WHERE Project__r.Name = '{project_name}'"
gates = requests.get(f"{instance_url}/services/data/v63.0/query", headers=headers, params={"q": gate_query}).json()

print("Gates API response:", gates)
print("\n")

query = "SELECT QualifiedApiName FROM EntityDefinition WHERE QualifiedApiName LIKE '%Gate%'"
response = requests.get(f"{instance_url}/services/data/v63.0/query", headers=headers, params={"q": query})
print(response.json())

for gate in gates["records"]:
    gate_id = gate["Id"]
    gate_name = gate["Name"]
    print(f"  🔹 Gate: {gate_name} ({gate_id})")

    # Get Documents linked to the Gate
    doclink_query = f"SELECT ContentDocumentId FROM ContentDocumentLink WHERE LinkedEntityId = '{gate_id}'"
    doclinks = requests.get(f"{instance_url}/services/data/v63.0/query",
                            headers=headers, params={"q": doclink_query}).json()

    for link in doclinks["records"]:
        doc_id = link["ContentDocumentId"]

        # Get Latest ContentVersion
        version_query = f"SELECT Id, Title, VersionData FROM ContentVersion WHERE ContentDocumentId = '{doc_id}' ORDER BY CreatedDate DESC LIMIT 1"
        version = requests.get(f"{instance_url}/services/data/v63.0/query",
                               headers=headers, params={"q": version_query}).json()


        if not version["records"]:
            continue

        file_id = version["records"][0]["Id"]
        file_name = version["records"][0]["Title"]
        file_url = f"{instance_url}/services/data/v63.0/sobjects/ContentVersion/{file_id}/VersionData"


        # Prepare full file path
        safe_project_name = sanitize_filename(project_name)
        safe_gate_name = sanitize_filename(gate_name)

        save_dir = os.path.join(base_download_dir, safe_project_name, safe_gate_name)
        os.makedirs(save_dir, exist_ok=True)
        total_folders_created.add(save_dir)

        current = datetime.now()
        new_file_name = f"{current.strftime('%Y-%m-%d_%H-%M-%S')}_{file_name}"
        save_path = os.path.join(save_dir, new_file_name)

        # Download and save file with error handling
        try:
            response = requests.get(file_url, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad HTTP status codes

            with open(save_path, "wb") as f:
                f.write(response.content)

            print(f"    ✅ Downloaded: {new_file_name}")
            total_files_downloaded += 1


        except requests.exceptions.RequestException as e:
            print(f"    ❌ Failed to download {new_file_name}: {e}")
        except IOError as e:
            print(f"    ❌ Failed to save {new_file_name}: {e}")

# ==== STEP 5: Write Summary Log ====
log_path = os.path.join(base_download_dir, "download_log.txt")
with open(log_path, "w") as log_file:
    log_file.write(f"Total folders created: {len(total_folders_created)}\n")
    log_file.write(f"Total files downloaded: {total_files_downloaded}\n")

print(f"\n🧾 Log file created at: {log_path}")
print(f"📦 Total folders: {len(total_folders_created)}, Total files: {total_files_downloaded}")