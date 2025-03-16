import requests
from django.conf import settings

MODEL_API_KEY="PGMPYXN-SYC4GB6-K1V3HNK-033FNHN" # AnythingLLM API Key
MODEL_SERVER_BASE_URL="http://localhost:3001/api/v1" # AnythingLLM API endpoint
WORKSPACE_SLUG="papersummarizer" # AnythingLLM API workspace

def auth(
    api_key: str,
    base_url: str,
) -> None:
    """
    Confirms the auth token is valid

    Inputs:
        - api_key (string): your api key
        - base_url (string): the endpoint of the AnythingLLM local server
    """
    auth_url = base_url + "/auth"

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + api_key
    }
    auth_response = requests.get(
        auth_url,
        headers=headers
    )

    if auth_response.status_code == 200:
        print("Successful authentication")
    else:
        print("Authentication failed")

    print(auth_response.json())

if __name__ == "__main__":

    # get the api_key and base_url from the config file
    # self.api_key = settings.MODEL_API_KEY
    # self.base_url = settings.MODEL_SERVER_BASE_URL
    api_key = MODEL_API_KEY
    base_url = MODEL_SERVER_BASE_URL


    # call the auth function
    auth(api_key, base_url)