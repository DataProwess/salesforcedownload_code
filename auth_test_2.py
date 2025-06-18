import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Salesforce OAuth configuration

# TOKEN_URL = "https://lendlease--uat.sandbox.my.salesforce.com/services/oauth2/token"
# TOKEN_URL = "https://lendlease.my.salesforce.com/services/oauth2/token" 

# TOKEN_URL="https://login.salesforce.com/services/oauth2/authorize?client_id=3MVG9WtWSKUDG.x5WeIq.ysfZLhOku.8gXr73g5AYkUDtP5MfW2YTMTLVKHrW.H5yZ4kDNMkPjS.wJ1UcAmdm&redirect_uri=https://login.salesforce.com/services/oauth2/success&response_type=code" 
# TOKEN_URL = "https://lendlease--c.vf.force.com/services/oauth2/token"
# TOKEN_URL = "https://lendlease.my.salesforce.com/app/mgmt/forceconnectedapps/forceAppDetail.apexp?applicationId=06POZ0000000JAj&applicationId=06POZ0000000JAj&id=0CiOZ00000004Wf/services/oauth2/token"
# TOKEN_URL = "https://test.salesforce.com/services/oauth2/token"  # Example for sandbox
# TOKEN_URL = "https://login.salesforce.com/services/oauth2/token"   
import urllib.parse

SF_CLIENT_ID = os.getenv("SF_CLIENT_ID")
SF_CALLBACK_URL = "https://login.salesforce.com/services/oauth2/success"  # Or your app's callback
SF_AUTH_URL = "https://login.salesforce.com/services/oauth2/authorize"

auth_params = {
    "response_type": "code",
    "client_id": SF_CLIENT_ID,
    "redirect_uri": SF_CALLBACK_URL,
    "scope": "api refresh_token"
}

auth_url = f"{SF_AUTH_URL}?{urllib.parse.urlencode(auth_params)}"
print(f"Authorization URL: {auth_url}")
