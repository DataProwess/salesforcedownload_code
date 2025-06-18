import csv
import os
import requests
from datetime import datetime
import re
from dotenv import load_dotenv

load_dotenv()

def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name)

# ==== CONFIGURATION ====
SF_CLIENT_ID = os.getenv("SF_CLIENT_ID")
SF_CLIENT_SECRET = os.getenv("SF_CLIENT_SECRET")
SF_USERNAME = os.getenv("SF_USERNAME")
SF_PASSWORD = os.getenv("SF_PASSWORD")
SF_SECURITY_TOKEN = os.getenv("SF_SECURITY_TOKEN")

# SharePoint Configuration
SHAREPOINT_CLIENT_ID = os.getenv("SHAREPOINT_CLIENT_ID")
SHAREPOINT_CLIENT_SECRET = os.getenv("SHAREPOINT_CLIENT_SECRET")
SHAREPOINT_TENANT_ID = os.getenv("SHAREPOINT_TENANT_ID")

SHAREPOINT_SITE_NAME = "https://lendlease.sharepoint.com/sites/Inflightprojecttest1" #os.getenv("SHAREPOINT_SITE_NAME")

# ==== AUTHENTICATION ====
# Salesforce Auth
auth_url = "https://lendlease--uat.sandbox.my.salesforce.com/services/oauth2/token"
auth_payload = {
    "grant_type": "password",
    "client_id": SF_CLIENT_ID,
    "client_secret": SF_CLIENT_SECRET,
    "username": SF_USERNAME,
    "password": SF_PASSWORD + SF_SECURITY_TOKEN
}

auth_response = requests.post(auth_url, data=auth_payload).json()
if "access_token" not in auth_response:
    raise Exception(f"Salesforce auth failed: {auth_response}")

access_token = auth_response["access_token"]
instance_url = auth_response["instance_url"]
sf_headers = {"Authorization": f"Bearer {access_token}"}

# SharePoint Auth
sharepoint_token_url = f"https://accounts.accesscontrol.windows.net/{SHAREPOINT_TENANT_ID}/tokens/OAuth/2"
sharepoint_auth_data = {
    "grant_type": "client_credentials",
    "client_id": SHAREPOINT_CLIENT_ID,
    "client_secret": SHAREPOINT_CLIENT_SECRET,
    "resource": "00000003-0000-0ff1-ce00-000000000000"
}
# ==== SharePoint Auth with Error Handling ====
try:
    sharepoint_token_response = requests.post(sharepoint_token_url, data=sharepoint_auth_data)
    sharepoint_token_response.raise_for_status()  # Check for HTTP errors
    sharepoint_token = sharepoint_token_response.json()["access_token"]
except requests.exceptions.HTTPError as http_err:
    print(f"❗ SharePoint auth HTTP error: {http_err}")
    print(f"❗ Server response: {sharepoint_token_response.text}")
    exit(1)
except KeyError:
    print("❗ Invalid SharePoint auth response - check credentials:")
    print(f"❗ Response received: {sharepoint_token_response.json()}")
    exit(1)
except Exception as e:
    print(f"❗ SharePoint auth failed: {str(e)}")
    exit(1)
sp_headers = {
    "Authorization": f"Bearer {sharepoint_token}",
    "Accept": "application/json;odata=verbose"
}

# ==== SHAREPOINT UPLOAD FUNCTION ====
def upload_to_sharepoint(file_content, file_name, folder_path):
    try:
        # Ensure folder path starts with document library
        full_path = f"/sites/{SHAREPOINT_SITE_NAME}/Shared%20Documents/{folder_path}"
        
        # Create folder structure if needed
        create_folder(full_path)
        
        # Upload file
        upload_url = f"https://{SHAREPOINT_SITE_NAME}/_api/web/GetFolderByServerRelativeUrl('{full_path}')/Files/add(url='{file_name}', overwrite=True)"
        response = requests.post(upload_url, headers=sp_headers, data=file_content)
        
        if response.status_code in [200, 201]:
            print(f"    ✅ Uploaded to SharePoint: {file_name}")
            return True
        else:
            print(f"    ❌ Upload failed ({response.status_code}): {file_name}")
            return False
            
    except Exception as e:
        print(f"    ❌ SharePoint upload error: {str(e)}")
        return False

def create_folder(folder_path):
    """Create folder structure in SharePoint if it doesn't exist"""
    try:
        check_url = f"https://{SHAREPOINT_SITE_NAME}/_api/web/GetFolderByServerRelativeUrl('{folder_path}')"
        requests.get(check_url, headers=sp_headers)
    except requests.exceptions.HTTPError:
        create_url = f"https://{SHAREPOINT_SITE_NAME}/_api/web/folders"
        payload = {
            "__metadata": { "type": "SP.Folder" },
            "ServerRelativeUrl": folder_path
        }
        requests.post(create_url, headers=sp_headers, json=payload)

# ==== MAIN PROCESSING ====
project_name = "Melbourne Quarter (Parent Project)"
sanitized_projectname = sanitize_filename(project_name)
total_files_uploaded = 0

print(f"\n📁 Processing Project: {project_name}")

# Get Gates for the Project
gate_query = f"SELECT Id, Name FROM LLCompass_Gate__c WHERE Project__r.Name = '{project_name}'"
gates = requests.get(f"{instance_url}/services/data/v63.0/query", headers=sf_headers, params={"q": gate_query}).json()

for gate in gates["records"]:
    gate_id = gate["Id"]
    gate_name = gate["Name"]
    print(f"  🔹 Processing Gate: {gate_name} ({gate_id})")

    # Get linked documents
    doclink_query = f"SELECT ContentDocumentId FROM ContentDocumentLink WHERE LinkedEntityId = '{gate_id}'"
    doclinks = requests.get(f"{instance_url}/services/data/v63.0/query",
                          headers=sf_headers, params={"q": doclink_query}).json()

    for link in doclinks["records"]:
        doc_id = link["ContentDocumentId"]

        # Get latest file version
        version_query = f"SELECT Id, Title, VersionData FROM ContentVersion WHERE ContentDocumentId = '{doc_id}' ORDER BY CreatedDate DESC LIMIT 1"
        version = requests.get(f"{instance_url}/services/data/v63.0/query",
                             headers=sf_headers, params={"q": version_query}).json()

        if not version["records"]:
            continue

        file_id = version["records"][0]["Id"]
        file_name = version["records"][0]["Title"]
        file_url = f"{instance_url}/services/data/v63.0/sobjects/ContentVersion/{file_id}/VersionData"

        try:
            # Download file content
            response = requests.get(file_url, headers=sf_headers)
            response.raise_for_status()
            
            # Prepare SharePoint path
            safe_gate_name = sanitize_filename(gate_name)
            sp_path = f"{sanitized_projectname}/{safe_gate_name}"
            
            # Upload to SharePoint
            if upload_to_sharepoint(response.content, file_name, sp_path):
                total_files_uploaded += 1

        except requests.exceptions.RequestException as e:
            print(f"    ❌ File download failed: {e}")
        except Exception as e:
            print(f"    ❌ Unexpected error: {e}")

print(f"\n✅ Process completed! Total files uploaded to SharePoint: {total_files_uploaded}")
