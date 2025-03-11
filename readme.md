## Python Application with Virtual Environment Setup

-----------------------------------------------

This application is a Python-based chatbot that integrates with Azure OpenAI, Databricks, and Chainlit. It provides functionalities like executing SQL queries on Databricks Genie and handling general AI tasks.

### Prerequisites

---------------

1. **Python**: Ensure you have Python 3.8 or higher installed.
2. **Virtual Environment**: Install `virtualenv` if not already installed:

```bash
pip install virtualenv
```

3. **Environment Variables**: Create a `.env` file in the project directory with the following keys and their respective values:

```plaintext
OPENAI_ENDPOINT=<your_openai_endpoint>
OPENAI_KEY=<your_openai_api_key>
OPENAI_VERSION=<your_openai_api_version>
OPENAI_DEPLOYMENT_NAME=<your_openai_deployment_name>
DATABRICKS_HOST=<your_databricks_host>
DATABRICKS_TOKEN=<your_databricks_token>
GENIE_SPACE_ID=<your_genie_space_id>
```


### Setup Instructions

--------------------

1. **Clone the Repository**:
Clone this repository to your local machine:

```bash
git clone <repository_url>
cd <repository_name>
```

2. **Create a Virtual Environment**:
Create and activate a virtual environment:

```bash
virtualenv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**:
Install the required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

4. **Prepare the `.env` File**:
Add your credentials and configuration values to the `.env` file as described in the prerequisites.

5. **Run the Application**:
Start the chatbot application using Chainlit:

```bash
chainlit run app.py -w
```


### File Structure

-----------------

- `app.py`: The main script for running the chatbot application.
- `requirements.txt`: Contains all necessary Python dependencies.
- `.env`: Stores environment variables (not included in the repository; create manually).
- `system_prompt.txt`: Contains the system prompt for the chatbot.


### Key Features

----------------

- **Azure OpenAI Integration**: Handles general LLM tasks like summarization, explanations, and more.
- **Databricks Genie Integration**: Executes SQL queries related to datasets.
- **Chainlit Framework**: Provides an interactive chatbot interface.


### System Prompt

----------------

The `system_prompt.txt` file contains a description that guides the OpenAI model's behavior. This prompt explains the context and functionality of the chatbot, including how to handle different types of queries. It provides instructions for the model to follow when generating responses, ensuring that the chatbot behaves as intended.

### Function Descriptions

------------------------

#### 1. `generate_sql_response`

- **Purpose**: This function generates a response to a natural language query by executing a SQL query on Databricks Genie. It is specifically designed to handle queries about the TCGA dataset so adapt it to your data, focusing on patient demographics, genomic mutations, clinical outcomes, cancer, and treatment effectiveness.
- **Parameters**:
    - `query`: A string representing the user's natural language input related to clinical, genomic, or treatment data from the TCGA dataset.
- **Usage**: This function is called when the chatbot identifies a query that requires structured data retrieval from the TCGA dataset.


#### 2. `handle_general_llm_task`

- **Purpose**: This function handles non-SQL tasks such as follow-up questions, summarization, explanations, biomedical concepts, AI-related topics, or general chatbot responses. It is used when the question is not directly related to data retrieval.
- **Parameters**:
    - `query`: A string representing the follow-up or general question, such as biomedical explanations.
- **Usage**: This function is called when the chatbot identifies a query that does not require SQL execution, such as general inquiries or follow-up questions.

### Note

-----

Adapt the description to your dataset !

### Dependencies

--------------

The application requires the following Python packages:

- `openai`
- `requests`
- `databricks-sdk`
- `chainlit`
- `python-dotenv`

These are listed in the `requirements.txt` file.

### Example `.env` File

----------------------

```plaintext
OPENAI_ENDPOINT=https://example-openai-endpoint.com
OPENAI_KEY=your_openai_key_here
OPENAI_VERSION=2023-03-15-preview
OPENAI_DEPLOYMENT_NAME=deployment_name_here
DATABRICKS_HOST=https://databricks-instance.com
DATABRICKS_TOKEN=your_databricks_token_here
GENIE_SPACE_ID=space_id_here
```


### Notes

-----

1. Ensure all required environment variables are correctly set in your `.env` file.
2. Replace placeholders in the `.env` file with actual credentials from your Azure OpenAI and Databricks accounts.
3. Use `chainlit` to run and interact with the chatbot.