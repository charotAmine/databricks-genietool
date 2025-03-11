import json
from openai import AzureOpenAI
import requests
from databricks.sdk import WorkspaceClient
import chainlit as cl
import os
from dotenv import load_dotenv
import time

load_dotenv()

openai_endpoint = os.getenv("OPENAI_ENDPOINT")
openai_key = os.getenv("OPENAI_KEY")
openai_version = os.getenv("OPENAI_VERSION")
openai_deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")
databricks_host = os.getenv("DATABRICKS_HOST")
databricks_token = os.getenv("DATABRICKS_TOKEN")
genie_space_id = os.getenv("GENIE_SPACE_ID")

client = AzureOpenAI(
    azure_endpoint = openai_endpoint, 
    api_key=openai_key,  
    api_version=openai_version
)

deployment_name = openai_deployment_name

w = WorkspaceClient(
        host=databricks_host,
        token=databricks_token
    )

file_path = "./system_prompt.txt"

with open(file_path, "r", encoding="utf-8") as file:
    system_prompt = file.read()


tools = [
    {
        "type": "function",
        "function": {
            "name": "generate_sql_response",
            "description": "Generate a response response from natural language input using Databricks Genie. This function is specifically designed to handle queries about the TCGA (The Cancer Genome Atlas) dataset. It should be used for retrieving structured data related to patient demographics, genomic mutations, clinical outcomes, cancer, and treatment effectiveness.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "User's natural language related to clinical, genomic, or treatment data from the TCGA dataset."
                    }
                },
                "required": ["query"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "handle_general_llm_task",
            "description": "Handles non-SQL tasks such as follow-up questions, summarization, explanations, biomedical concepts, AI-related topics, or general chatbot responses. This function should be used when the question is not directly related to data retrieval.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The follow-up or general question, such as biomedical explanations."
                    }
                },
                "required": ["query"],
            },
        }
    }
]

async def execute_genie_query(query ,w ) -> str :
    """Executes a Genie query and polls until completion."""
    current_user = w.current_user.me()
    print(f"Authenticated as: {current_user.user_name} (ID: {current_user.id})")
    space_id = genie_space_id

    headers = {"Authorization": "Bearer {}".format(databricks_token)}
    try:
        conversation_id = cl.user_session.get("conversation_id")
        while conversation_id is None:
            time.sleep(5)
            conversation_id = cl.user_session.get("conversation_id")
        
        conversation = w.genie.create_message_and_wait(space_id, conversation_id,content=query)
        message_id = conversation.id
        print("here",message_id)
        response = w.genie.execute_message_query(space_id, conversation_id, message_id)
        print(response)
        data_context = conversation.attachments[0].query.description
        full_request = f"{databricks_host}api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}/query-result"
        response = requests.get(full_request, headers=headers)
        columns = response.json()['statement_response']['manifest']['schema']['columns']
        data_values = response.json()['statement_response']['result']['data_typed_array']

        result = f"[context] : {data_context} --- [Data Columns] : {columns} --- [Data Values] : {data_values}"
        print(result)
        return result
    except Exception as e:
        print(f"Error: {str(e)}")

        return f"Error: {str(e)}"


async def execute_follow_up(query):
    messages = [{"role": "user", "content": query}]

    response = client.chat.completions.create(
        model=deployment_name,
        messages=messages
    )

    response_message = response.choices[0].message.content

    return response_message

async def handle_message(message: cl.Message):
    chat_history = cl.user_session.get("chat_history")

    messages = [
        {"role": "system", "content": system_prompt},
    ] + chat_history + [{"role": "user", "content": message.content}]
    
    print(messages)
    response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    response_message = response.choices[0].message
    messages.append(response_message)

    if response_message.tool_calls:
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            print(f"Function call: {function_name}")
            print(f"Function arguments: {function_args}")

            if function_name == "generate_sql_response":
                function_response = await execute_genie_query(
                    query=function_args.get("query"),
                    w=w 
                )
            elif function_name == "handle_general_llm_task":
                function_response = await execute_follow_up(
                    query=function_args.get("query")
                )
            else:
                function_response = json.dumps({"error": "Unknown function"})

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            })

    final_response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
    )
    return final_response.choices[0].message.content

@cl.on_message
async def on_message(message: cl.Message):
    chat_history = cl.user_session.get("chat_history")

    chat_history.append({"role": "user", "content": message.content})

    # Process the message and get the AI's response
    response = await handle_message(message)

    chat_history.append({"role": "assistant", "content": response})

    cl.user_session.set("chat_history", chat_history)

    await cl.Message(content=response).send()


@cl.on_chat_start
async def on_chat_start():
    w = WorkspaceClient(
        host=databricks_host,
        token=databricks_token
    )
    conversation = w.genie.start_conversation_and_wait(genie_space_id, content="")
    cl.user_session.set("chat_history", [])
    cl.user_session.set("conversation_id", conversation.conversation_id)
    welcome_message = "Welcome to the chatbot. How can I assist you today?"
    msg = cl.Message(content=welcome_message)
    await msg.send()

# Run Chainlit
cl.instrument_openai()
