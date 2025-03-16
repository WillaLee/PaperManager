## PaperEdge: On-Device Academic Paper Management with AI

A comprehensive tool for managing academic papers, featuring AI-driven summarization, categorization assistance, citation management, text-to-speech (TTS), and multi-format exports. The system runs locally using ONNX Runtime for optimized performance while ensuring data privacy.

# Features

## Core Functionalities

- **Upload & Extract**: Supports PDF uploads, extracting text and metadata.

- **AI-Powered Summarization(RAG-Enhanced)**: 
  - **Technology**: Uses Llama 3.2 via AnythingLLM for on-device processing.  
  - **Accuracy**: Retrieval-Augmented Generation (RAG) ensures context-aware summaries with minimal hallucinations.  

- **Categorization Assistance**:  
  - Automatically suggests relevant labels based on content.  
  - Allows manual tagging and custom categorization.

- **Write Citation**:  
  - Extracts metadata (DOI, authors, journal, etc.).  
  - Generates and exports references in BibTeX format for LaTeX compatibility.  
  - Provides an interactive UI to edit and validate citations.
  - Checks H-index to assess the credibility of sources and determine if they are worth citing.

- **Text-to-Speech (TTS)**: Converts summaries into natural-sounding speech for accessibility and multitasking.

## Export Options

- **LaTeX & BibTeX Export**: Convert summaries and citations to LaTeX/BibTeX format.
- **Multi-Format Export**: Save results as Markdown, plain text, or JSON for integration with other tools.

# Demo
## Watch a quick demo of Paper Manager in action:


# Authors
team: 360HackAI

# Backend Installation

1. Clone the repository:

```
git clone https://github.com/WillaLee/PaperManager.git
cd PaperManager
```

2. Create a python virtual environment and install required python modules.

```python
python3 -m venv .venv
source .venv/bin/activate # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure the database
    Option 1: Using Local PostgreSQL
    1. Log in to PostgreSQL:
    ```bash
    psql -U postgres
    ```
    2. create a new database for this project
    ```sql
    CREATE DATABASE papermanager_db;
    ```
    Option 2: Using Docker
    1. Run a PostgreSQL container:
    ```bash
    docker run --name papermanager-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=papermanager_db -p 5432:5432 -d postgres:latest
    ```
4.  Set up environment variables
    Create a .env file in the PaperManager directory:
    ```
    DB_NAME=papermanager_db
    DB_USER=postgres
    DB_PASSWORD=postgres  # Change if necessary
    DB_HOSTNAME=127.0.0.1  # Use 'localhost' if running Docker on Linux or WSL2
    DB_PORT=5432
    MODEL_API_URL=http://localhost:3001/api/generate  # AnythingLLM API endpoint
    ```

5. Run the database migrations

```python
python manage.py migrate
```

5. Start the application

```python
python manage.py runserver
```
# Frontend Installation

1. Navigate to the frontend directory

```python
cd ../frontend
```

2. Install dependencies
```python
npm install
```

3. Start the React app
```python
npm start
```

# Model Deployment
1. Set up AnythingLLM
2. Start the AnythingLLM server
```
anythingllm start
```
3. Verify API Connection
   - Ensure the API URL matches the MODEL_API_URL in .env.
   - If running on a remote server, update the .env file with the correct endpoint.

# Usage (Prompts) 
- Upload research paper (PDF)
- Generate AI-powered summary
- Edit tags/categories (optional)
- Generate citation
- Export results or convert to speech

## License
This project is licensed under the [MIT License](LICENSE.md)