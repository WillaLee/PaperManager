import requests
import sys
import threading
import time
import json
import logging
import os
from django.conf import settings

MODEL_API_KEY="PGMPYXN-SYC4GB6-K1V3HNK-033FNHN" # AnythingLLM API Key
MODEL_SERVER_BASE_URL="http://localhost:3001/api/v1" # AnythingLLM API endpoint
WORKSPACE_SLUG="papersummarizer" # AnythingLLM API workspace

def loading_indicator() -> None:
    """
    Display a loading indicator in the console while the chat request is being processed
    """
    while not stop_loading:
        for _ in range(10):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.5)
        sys.stdout.write('\r' + ' ' * 10 + '\r')
        sys.stdout.flush()
    print('')

class Chatbot:
    def __init__(self):
        '''
        self.api_key = settings.MODEL_API_KEY
        self.base_url = settings.MODEL_SERVER_BASE_URL
        self.workspace_slug = settings.WORKSPACE_SLUG
        '''
        self.api_key = MODEL_API_KEY
        self.base_url = MODEL_SERVER_BASE_URL
        self.workspace_slug = WORKSPACE_SLUG

        self.chat_url = f"{self.base_url}/workspace/{self.workspace_slug}/chat"
        self.upload_url = f"{self.base_url}/document/upload"
        self.move_url = f"{self.base_url}/workspaces/{self.workspace_slug}/documents/move"

        self.message_history = []

    def run(self) -> None:
        """
        Run the chat application loop. The user can type messages to chat with the assistant.
        """
        while True:
            user_message = input("You: ")
            if user_message.lower() in ["exit", "quit"]:
                break
            try:
                print("Agent: " + self.chat(user_message))
            except Exception as e:
                print("Error! Check the model is correctly loaded. More details in README troubleshooting section.")
                sys.exit(f"Error details: {e}")
                

    def chat(self, message: str) -> str:
        """
        Send a chat request to the model server and return the response
        
        Inputs:
        - message: The message to send to the chatbot
        """
        global stop_loading
        stop_loading = False
        loading_thread = threading.Thread(target=loading_indicator)
        loading_thread.start()

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.api_key
        }
        

        self.message_history.append({
            "role": "user",
            "content": message
        })

        # create a short term memory bank with the last 20 messages
        short_term_memory = self.message_history[-20:]

        data = {
            "message": message,
            "mode": "chat", # change to query if possible
            "sessionId": "example-session-id",
            "attachments": [],
            "history": short_term_memory
        }

        chat_response = requests.post(
            self.chat_url,
            headers=headers,
            json=data
        )

        stop_loading = True
        loading_thread.join()

        try:
            text_response = chat_response.json()['textResponse']
            self.message_history.append({
                "role": "assistant",
                "content": text_response
            })
            return text_response
        except ValueError:
            return "Response is not valid JSON"
        except Exception as e:
            return f"Chat request failed. Error: {e}"


    def get_summary(self, paper_name):
        prompt = f"Give me the summary of the paper: {paper_name}"
        summary = self.chat(prompt)
        
        print("\nGenerated Summary:")
        print(summary)
        return str(summary)
    
    def get_keywords(self, paper_name):
        """Get the top 5 keywords of a paper as a list of strings."""
        prompt = f"Give me exactly 5 keywords for the paper '{paper_name}', separated by commas. Do not include any explanations."
        
        keywords_response = self.chat(prompt)
        
        # Print raw response for debugging
        print("\nRaw Chatbot Response:", keywords_response)

        # Ensure response is a string and split into a list
        if isinstance(keywords_response, str):
            keywords_list = [keyword.strip() for keyword in keywords_response.split(",")]
        else:
            keywords_list = []

        print("\nGenerated Keywords List:", keywords_list)
        return keywords_list  # Returns a list of strings

    
    def upload_research_paper(self, pdf_file):
        """ Uploads a research paper to AnythingLLM's RAG and returns its JSON location. """
        try:
            logging.info(f"Uploading research paper: {pdf_file}")

            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }

            # Prepare the file for upload
            files = {'file': pdf_file}
            response = requests.post(self.upload_url, headers=headers, files=files)

            if response.status_code == 200:
                response_data = response.json()
                logging.info("File uploaded successfully.")
                print("File uploaded successfully.")

                # Extract correct document JSON path for moving it
                document_location = response_data["documents"][0]["location"]
                logging.info(f"Uploaded document location: {document_location}")

                return document_location  # Return correct JSON path
            else:
                logging.error(f"Failed to upload file: {response.text}")
                print(f"Failed to upload file: {response.text}")
                return None

        except Exception as e:
            logging.error(f"Error uploading file: {e}")
            print(f"Error uploading file: {e}")
            return None
    
    def move_file_to_workspace(self, document_location):
        """ Moves an uploaded document to a workspace in AnythingLLM. """
        try:
            if not document_location:
                logging.error("Document location is required to move the file.")
                print("Error: Document location is missing.")
                return

            logging.info(f"Moving document {document_location} to workspace {self.workspace_slug}")

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # The API requires an array of document locations
            data = {"adds": [document_location]}

            workspace_url = f"{self.base_url}/workspace/{self.workspace_slug}/update-embeddings"
            response = requests.post(workspace_url, headers=headers, json=data)

            if response.status_code == 200:
                logging.info("Document moved successfully.")
                print("Document moved successfully.")
            else:
                logging.error(f"Failed to move document: {response.text}")
                print(f"Failed to move document: {response.text}")

        except Exception as e:
            logging.error(f"Error moving document: {e}")
            print(f"Error moving document: {e}")
    
    def add_paper_to_rag(self, pdf_file):
        document_location = self.upload_research_paper(pdf_file)
        self.move_file_to_workspace(document_location)
    
    # Provide an IEEE citation for the paper
    def get_citations(self, paper_name):
        prompt = f"Provide an IEEE citation for the paper: {paper_name}"
        citation = self.chat(prompt)
        print("\nGenerated IEEE Citation:")
        print(citation)

    
# For debug
if __name__ == '__main__':
    stop_loading = False
    chatbot = Chatbot()
    # chatbot.run()
    # file_path = "/Users/joshua/Desktop/simple-npu-chatbot-main/test_input/Attension is all you need.json"
    # file_path = "/Users/joshua/Desktop/simple-npu-chatbot-main/test_input/attention is all you need.pdf"
    # file_path = r"C:\Users\qc_de\PaperManager\media\papers\Attention Is All You Need.pdf"
    # document_location = chatbot.upload_research_paper(file_path)
    # chatbot.move_file_to_workspace(document_location)
    # chatbot.get_summary("Attention is all you need")
    # chatbot.get_keywords("Attention is all you need")
    # with open(file_path, 'rb') as file:
    #    chatbot.add_paper_to_rag(file)
    
    chatbot.get_citations("Attention is all you need")
    stop_loading = True
    