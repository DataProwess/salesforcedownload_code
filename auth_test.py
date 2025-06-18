import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Salesforce OAuth configuration

# TOKEN_URL = "https://lendlease--uat.sandbox.my.salesforce.com/services/oauth2/token"
TOKEN_URL = "https://lendlease.my.salesforce.com/services/oauth2/token" 

# TOKEN_URL="https://login.salesforce.com/services/oauth2/authorize?client_id=3MVG9WtWSKUDG.x5WeIq.ysfZLhOku.8gXr73g5AYkUDtP5MfW2YTMTLVKHrW.H5yZ4kDNMkPjS.wJ1UcAmdm&redirect_uri=https://login.salesforce.com/services/oauth2/success&response_type=code" 
# TOKEN_URL = "https://lendlease--c.vf.force.com/services/oauth2/token"
# TOKEN_URL = "https://lendlease.my.salesforce.com/app/mgmt/forceconnectedapps/forceAppDetail.apexp?applicationId=06POZ0000000JAj&applicationId=06POZ0000000JAj&id=0CiOZ00000004Wf/services/oauth2/token"
# TOKEN_URL = "https://test.salesforce.com/services/oauth2/token"  # Example for sandbox
# TOKEN_URL = "https://login.salesforce.com/services/oauth2/token"   

def get_salesforce_token():
    try:
        SF_CLIENT_ID = os.getenv("SF_CLIENT_ID")
        SF_CLIENT_SECRET = os.getenv("SF_CLIENT_SECRET")
        SF_USERNAME = os.getenv("SF_USERNAME")
        SF_PASSWORD = os.getenv("SF_PASSWORD")
        SF_SECURITY_TOKEN = os.getenv("SF_SECURITY_TOKEN")  # Optional, only if needed
        print(f"SF_CLIENT_ID: {SF_CLIENT_ID}")
        print(f"SF_CLIENT_SECRET: {SF_CLIENT_SECRET}")  
        print(f"SF_USERNAME: {SF_USERNAME}")
        print(f"SF_PASSWORD: {SF_PASSWORD}")
        print(f"SF_SECURITY_TOKEN: {SF_SECURITY_TOKEN}")
        
        payload = {
            "grant_type": "password",
            # "response_type": "code",
            "client_id": SF_CLIENT_ID,
            "client_secret": SF_CLIENT_SECRET,
            "username": SF_USERNAME, 
            "password": SF_PASSWORD + SF_SECURITY_TOKEN 
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(TOKEN_URL, data=payload, headers=headers)
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response content: {response.text}")
        # Check if the response is successful
        if response.status_code != 200:
            print(f"Failed to authenticate: {response.status_code} - {response.content}")
            response.raise_for_status()
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print("Response content:", e.response.text)
        return None

if __name__ == "__main__":
    token_data = get_salesforce_token()
    if token_data:
        print("Access Token:", token_data['access_token'])
        print("Instance URL:", token_data['instance_url'])
        print("Token Type:", token_data['token_type'])
    else:
        print("Failed to authenticate")
