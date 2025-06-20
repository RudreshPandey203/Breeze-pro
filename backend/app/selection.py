import time
import os
from dotenv import load_dotenv
from openai import OpenAI
from langchain.agents.openai_assistant import OpenAIAssistantRunnable
def test():
    print("hello")

def classify(input):
    load_dotenv()
    api_key = os.environ['OPENAI_API_KEY']

    # Initialize the OpenAI client
    client = OpenAI(api_key=api_key)


    assistantDeveloper = client.beta.assistants.create(
        name="",
        instructions='''You are a problem classifier and your task is to read from the instruction of users and then after understanding it classifiy it into its best posssible category.You should also make sure that if any indirect questions are asked your task is to classify it to the best possible category.
                            for example, if user is asking to send mails, send 1, 
                            if user is asking to get mails, send 2,
                            if user is asking to create database, send 3,
                            if user is asking to create a project and deploy it, send 4,
                            if user is asking to create a notepad with those details, send 5,
                            ''',
        model="gpt-4-0125-preview",
        )

    thread = client.beta.threads.create()

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=input,
    )

    # Create the Run, passing in the thread and the assistant
    run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistantDeveloper.id
    )

    # Periodically retrieve the Run to check status and see if it has completed
    # Should print "in_progress" several times before completing
    while run.status != "completed":
        keep_retrieving_run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        print(f"Run status: {keep_retrieving_run.status}")

        if keep_retrieving_run.status == "completed":
            print("\n")
            break

    # Retrieve messages added by the Assistant to the thread
    all_messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )

    # Print the messages from the user and the assistant
    print("###################################################### \n")
    print(f"USER: {message.content[0].text.value}")
    print(f"ASSISTANT: {all_messages.data[0].content[0].text.value}")


