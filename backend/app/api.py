from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import File, UploadFile
from pydantic import BaseModel
import json

import time
import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import subprocess

import time
import os
from dotenv import load_dotenv
from openai import OpenAI
from langchain.agents.openai_assistant import OpenAIAssistantRunnable
# from selection import classify,test



#selection.py
import time
import os
from dotenv import load_dotenv
from openai import OpenAI
from langchain.agents.openai_assistant import OpenAIAssistantRunnable

import imaplib
import email
from email.header import decode_header

load_dotenv()
api_key = os.environ['OPENAI_API_KEY']

#Devin
import time
import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import subprocess

# Load the API key from an environment variable
def devin_beta(input):
    load_dotenv()
    api_key = os.environ['OPENAI_API_KEY']

    # Initialize the OpenAI client
    client = OpenAI(api_key=api_key)

    # Define base directory and API
    base_dir = r'/Users/rudreshpandey/Desktop/WebD/Working/Breazer-web/projects'
    scope_name = "kumar-shivams-projects-1bfeb636"
    project_name = datetime.now().strftime("%Y%m%d_%H%M%S")



    # Create assistants (the API and method might differ based on OpenAI's latest updates)
    assistantDeveloper = client.beta.assistants.create(
        name="Developer",
        instructions="Create a single HTML file named \"index.html\" that incorporates HTML, CSS, and JavaScript within the file itself. Ensure that no external references to CSS or JavaScript files are made. The HTML file should contain a complete and robust structure, encompassing all necessary elements for a web project. Embed the CSS styles directly within the <style> tags and embed the JavaScript code within the <script> tags. The CSS should be meticulously crafted to enhance the aesthetics and layout of the webpage, while the JavaScript should provide full functionality as requested by the user. The HTML file should stand alone, containing all the necessary code for a fully functional and visually appealing web project.",
        model="gpt-4-0125-preview",
    )

    thread=client.beta.threads.create()

    assistantRewriter = client.beta.assistants.create(
        name="Rewriter",
        instructions="Your task is to create a flow which include steps to implement the task given .",
        model="gpt-4-0125-preview",
    )




    def runAssistant(assistant_id,thread_id,user_instructions):
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            instructions=user_instructions,
        )

        while True:
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

            if run.status == "completed":
                print("This run has completed!")

                break
            else:
                print("in progress...")
                time.sleep(5)

    def create_and_write_file(data):
        # Generate a unique folder name using the current date and time
        now = datetime.now()
        folder_name = now.strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS

        # Define the base directory and construct the full path for the new folder
        base_dir = r'/Users/rudreshpandey/Desktop/WebD/Working/Breazer-web/projects'
        new_folder_path = os.path.join(base_dir, folder_name)

        # Create the new folder
        os.makedirs(new_folder_path, exist_ok=True)

        # Path to the index.html file in the new folder
        file_path = os.path.join(new_folder_path, 'index.html')

        # Write data to the index.html file with UTF-8 encoding
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(data)

        print(f"File has been created and data has been written to {file_path}")

        # Execute the npx vercel command
        # Change the working directory to the new folder
        os.chdir(new_folder_path)

        # Run 'npx vercel' command in interactive mode and keep the terminal open
        subprocess.run("npx vercel", shell=True, check=True)

        
    def format_html_input(input_text: str) -> str:
        # Split the input text by new lines and filter out any non-HTML lines
        input_lines = input_text.split('\n')
        html_lines = []
        in_html_block = False

        for line in input_lines:
            # Detect the start and end of the HTML block
            if line.strip().startswith('<!DOCTYPE html>'):
                in_html_block = True
            if in_html_block:
                html_lines.append(line)
            if line.strip().endswith('</html>'):
                in_html_block = False

        # Join the HTML lines into a single string and return it
        formatted_html = '\n'.join(html_lines)
        return formatted_html

    print("Please give your instructions: ")
    # user_instructions = input.capture_voice_input()
    text=input+"Make sure it has all HTML, CSS, and JavaScript code embedded within the file itself.There nust be a javascript and css code"

    # Run the Writer Assistant to create a first draft
    print("Writer: \n")                      
    runAssistant(assistantDeveloper.id,thread.id,text)
                    
    # # Have the Writer Assistant rewrite the first chapter based on the feedback from the Critic
    # print("Rewrite: \n")        
    # runAssistant(assistantRewriter.id,thread.id,""" For the given input create a 10 step flow to complete this project. """)

    messages = client.beta.threads.messages.list(thread_id=thread.id)

    # Save the text of the messages so that they can be printed in reverse order
    messageStore = []

    for message in messages:
        if message.assistant_id == assistantDeveloper.id:
            assistantName = "Writer: "
        else:
            continue
            
        messageStore.append(message.content[0].text.value)

    #To make it more readable print the messages in reversed order 
    output=""

    for message in reversed(messageStore):
        output+=format_html_input(message)
        # print(output)
        file_path = r'/Users/rudreshpandey/Desktop/WebD/Working/Breazer-web/projects'
        create_and_write_file(output)
        print(f"File has been created and data has been written to {file_path}")
#Devin beta

# Initialize the OpenAI client
client = OpenAI(api_key=api_key)
def classify(input):
    assistantDeveloper = client.beta.assistants.create(
        name="",
        instructions='''You are a problem classifier and your task is to read from the instruction of users and then after understanding it classifiy it into its best posssible category.You should also make sure that if any indirect questions are asked your task is to classify it to the best possible category.
                            for example, if user is asking to send mails, send 1, 
                            if user is asking to get mails, send 2,
                            if user is asking to create database, send 3,
                            if user is asking to create a project and deploy it, send 4,
                            if user is asking to create a notepad with those details, send 5, if user is asking any other thing not related to any of these, send 6
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
    return all_messages.data[0].content[0].text.value
#selection.py ends here

#mail send steps maker
def jsonSteps(input):
    json_convertor= client.beta.assistants.create(
        name="jsonwa",
        instructions='''I will send you a process, and break it into steps corresponding to the text provided that how the process mentioned in text can be automated and how computer will do all other task and its process and return the steps in json format in an array. For example, if i ask to send a complain to a website, list out the steps how it can be done by opening their website, lodging complain, etc , for another example if i ask to make a recipe for any food item, show the steps to be followed, example if i ask yo you to send a mail to someone, you should write about the processes needed to be carried on to automate the process so that it can be achieved in steps it like you are doing it by opening the mail of xyz@gmail.com in reference to text, typing the message, reviewing it , sending it etc., other than these example, if you get any other problem, just write the steps to be followed to do the work and return it in json format with variable name as steps. The steps should be in json format as like I have to directly pass it in api call json : {"abc", "abc"}. Send in raw text and strictly not in markdown text''',
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
    assistant_id=json_convertor.id
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
    # print("###################################################### \n")
    # print(f"USER: {message.content[0].text.value}")
    # print(f"ASSISTANT: {all_messages.data[0].content[0].text.value}")
    return all_messages.data[0].content[0].text.value

#mail send steps maker ends here

## Mail format provider
def jsonBody(input):
    json_convertor= client.beta.assistants.create(
        name="jsonwa",
        instructions='''i ll send you a text about sending a mail to someone fetch the my name, name of receiver, emailid (in lower) , subject and body from the text and return it in a array with variable name as sender_name, reciever_name, body, subject, email in format {"sender_name":<sender-name>, "reciever_name":<reciever_name> (so and so )}. Send in raw text and strictly not in markdown text''',
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
    assistant_id=json_convertor.id
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
    # print("###################################################### \n")
    # print(f"USER: {message.content[0].text.value}")
    # print(f"ASSISTANT: {all_messages.data[0].content[0].text.value}")
    return all_messages.data[0].content[0].text.value

#mail reader

#mail reader bot
def jsonKeyword(input):
    json_convertor= client.beta.assistants.create(
        name="jsonwa",
        instructions='''I will send you the text about sorting the mail on some basis, find the keyword i am searching for and return it in a json form with variable name as keyword strictly in raw format as {"keyword":<keyword>} and not strictly not in markdown text.''',
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
    assistant_id=json_convertor.id
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
    # print("###################################################### \n")
    # print(f"USER: {message.content[0].text.value}")
    # print(f"ASSISTANT: {all_messages.data[0].content[0].text.value}")
    print("key is getting returned as : ",all_messages.data[0].content[0].text.value)
    return all_messages.data[0].content[0].text.value

#mail reader bot ends here

import imaplib
import email
from email.header import decode_header

# Function to decode email headers
def mail_fetch(input):
    def decode_subject(subject):
        decoded = decode_header(subject)[0][0]
        if isinstance(decoded, bytes):
            return decoded.decode('utf-8')
        else:
            return decoded

    # IMAP server configuration
    IMAP_SERVER = 'imap.gmail.com'
    IMAP_PORT = 993
    print(os.environ['Email'])
    print(os.environ['Password'])
    EMAIL_ADDRESS = os.environ['Email']
    PASSWORD = os.environ['Password']
    SEARCH_TEXT = input  # Text to search for in subject or sender

    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)

    # Login to the server
    mail.login(EMAIL_ADDRESS, PASSWORD)

    # Select the inbox
    mail.select('inbox')

    # Search for emails containing the keyword "exciting" in the body, name, or subject
    status, email_ids = mail.search(None, f'(OR BODY "{SEARCH_TEXT}" FROM "{SEARCH_TEXT}" SUBJECT "{SEARCH_TEXT}")')

    if status == 'OK':
        email_ids = email_ids[0].split()
        print("Number of Emails Found:", len(email_ids))  # Debugging statement

        for email_id in email_ids:
            # Fetch the email
            status, email_data = mail.fetch(email_id, '(RFC822)')
            print("Fetch Status:", status)  # Debugging statement
            
            if status == 'OK':
                raw_email = email_data[0][1]

                # Ensure raw_email is bytes
                if isinstance(raw_email, bytes):
                    # Parse the raw email
                    msg = email.message_from_bytes(raw_email)
                else:
                    # Parse the raw email by encoding it to bytes
                    msg = email.message_from_bytes(raw_email.encode('utf-8'))

                # Extract email headers
                subject = decode_subject(msg['subject'])
                sender = decode_header(msg['from'])[0][0]
                date = msg['date']
                
                # Print email details
                print(f"Subject: {subject}")
                print(f"From: {sender}")
                print(f"Date: {date}")
                print()

    # Logout from the server
    mail.logout()
#mail reader ends here


app = FastAPI()

origins = [
    "http://localhost:3000",
    "localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class MessageIn(BaseModel):
    message: str

@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to your todo list."}

@app.post("/upload_audio/")
async def upload_audio(audio_file: UploadFile = File(...)):
    return {"res":0}

@app.post("/transcript")
async def transcript(message_in: MessageIn):
    print("hello")
    print("Message:", message_in.message) 
    res = classify(message_in.message)
    print("Result code =", res)
    steps = jsonSteps(message_in.message)
    print(steps)
    if(res=='4'):
        devin_beta(message_in.message)
    return {"req":res, "steps":steps}
@app.post("/sendmail")
async def send_mail(message_in: MessageIn):
    print("mail format")
    jsonres = jsonBody(message_in.message)
    print(jsonres)
    return {"jsonres": jsonres}
    # elif res == '2':
    #     print("result fetch")
    #     keyword = jsonKeyword(message_in.message)
    #     print("keyword =", keyword)
    #     jsonres = mail_reader(keyword)
    #     print("Result =", jsonres)
    #     return {"req": res, "jsonres": jsonres}
    # else:
    #     return {"req": res}

@app.post("/fetchmail")
async def fetch_mail(message_in:MessageIn):
    print("mail fetch")
    key = jsonKeyword(message_in.message)
    print("hello")
    key1 = json.loads(key)
    key2 = key1["keyword"]
    print(key2)
    mail_fetch(key2)
    return {"res":"ok"}


@app.get("/abort")
async def abort():
    print("process aborted")
    return {"message":"process aborted"}


#     print("process aborted")
#     return {"message":"process aborted"}