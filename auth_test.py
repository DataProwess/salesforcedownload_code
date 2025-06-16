import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Salesforce OAuth configuration
SF_DOMAIN = 'lendlease.my.salesforce.com'
TOKEN_URL = f'https://{SF_DOMAIN}/services/oauth2/token'

def get_salesforce_token():
    try:
        # Construct password with security token
        password = os.getenv('SF_PASSWORD') + os.getenv('SF_SECURITY_TOKEN')
        
        payload = {
            'grant_type': 'password',
            'client_id': os.getenv('SF_CLIENT_ID'),
            'client_secret': os.getenv('SF_CLIENT_SECRET'),
            'username': os.getenv('SF_USERNAME'),
            'password': password
        }

        response = requests.post(TOKEN_URL, data=payload)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    token_data = get_salesforce_token()
    if token_data:
        print("Access Token:", token_data['access_token'])
        print("Instance URL:", token_data['instance_url'])
        print("Token Type:", token_data['token_type'])
    else:
        print("Failed to authenticate")
