import requests
# import yaml
from prettyprinter import pprint
MODEL_API_KEY="PGMPYXN-SYC4GB6-K1V3HNK-033FNHN" # AnythingLLM API Key
MODEL_SERVER_BASE_URL="http://localhost:3001/api/v1" # AnythingLLM API endpoint

def workspaces(
    api_key: str,
    base_url: str
) -> None:
    """
    Prints formatted json info about the available workspaces. Used
    to identify the correct workspace slug for the chat api call.

    Inputs:
        - api_key (string): your api key
        - base_url (string): the endpoint of the AnythingLLM local server
    """
    workspaces_url = base_url + "/workspaces"

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key
    }

    workspaces_response = requests.get(
        workspaces_url,
        headers=headers
    )

    if workspaces_response.status_code == 200:
        print("Successful authentication")
    else:
        print("Authentication failed")

    pprint(workspaces_response.json())

if __name__ == "__main__":

    # get the api_key and base_url from the config file
    api_key = MODEL_API_KEY
    base_url = MODEL_SERVER_BASE_URL

    # call the workspaces function
    workspaces(api_key, base_url)