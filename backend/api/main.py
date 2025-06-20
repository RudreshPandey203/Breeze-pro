from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import os
import time
import subprocess
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv
from openai import AzureOpenAI
from datetime import datetime

# Initialize environment and Azure client
load_dotenv()
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-05-01-preview",
    azure_endpoint=os.getenv("AZURE_ENDPOINT")
)

# Devin Beta Implementation
def devin_beta(input):
    base_dir = r'/Users/rudreshpandey/Desktop/work/ResumeProjects/Breeze/projects'
    scope_name = "kumar-shivams-projects-1bfeb636"
    project_name = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create Azure OpenAI assistant
    assistantDeveloper = client.beta.assistants.create(
        name="Developer",
        instructions="Create a single HTML file named \"index.html\" with embedded CSS/JS",
        model="gpt-4o",
    )

    thread = client.beta.threads.create()
    text = f"{input} Make sure it has all HTML, CSS, and JavaScript code embedded within the file itself."

    def run_assistant(assistant_id, thread_id, user_instructions):
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            instructions=user_instructions,
        )

        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id, 
                run_id=run.id
            )
            if run.status == "completed":
                break
            time.sleep(5)

    def create_and_write_file(data):
        new_folder_path = os.path.join(base_dir, project_name)
        os.makedirs(new_folder_path, exist_ok=True)
        file_path = os.path.join(new_folder_path, 'index.html')
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(data)
        
        os.chdir(new_folder_path)
        subprocess.run("npx vercel", shell=True, check=True)

    def format_html_input(input_text: str) -> str:
        input_lines = input_text.split('\n')
        html_lines = []
        in_html_block = False

        for line in input_lines:
            if line.strip().startswith('<!DOCTYPE html>'):
                in_html_block = True
            if in_html_block:
                html_lines.append(line)
            if line.strip().endswith('</html>'):
                in_html_block = False

        return '\n'.join(html_lines)

    run_assistant(assistantDeveloper.id, thread.id, text)
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    
    output = ""
    for message in reversed(messages.data):
        if message.role == "assistant":
            formatted = format_html_input(message.content[0].text.value)
            output += formatted
    
    create_and_write_file(output)
    return True

# Classification System
def classify(input):
    assistant = client.beta.assistants.create(
        name="Classifier",
        instructions='''Classify requests into:
        1 - Send mail
        2 - Get mail
        3 - Create database
        4 - Create+deploy project
        5 - Create notepad
        6 - Other
        only return the number associated and nothing else.''',
        model="gpt-4o",
    )

    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=input,
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    while run.status != "completed":
        time.sleep(2)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    print(messages)
    return messages.data[0].content[0].text.value

# Email Processing Functions
def jsonSteps(input):
    assistant = client.beta.assistants.create(
        name="StepGenerator",
        instructions="Break processes into JSON steps",
        model="gpt-4o",
    )

    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=input,
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    while run.status != "completed":
        time.sleep(2)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return messages.data[0].content[0].text.value

def jsonBody(input):
    assistant = client.beta.assistants.create(
        name="MailParser",
        instructions="Extract email components to JSON",
        model="gpt-4o",
    )

    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=input,
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    while run.status != "completed":
        time.sleep(2)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return messages.data[0].content[0].text.value

def jsonKeyword(input):
    assistant = client.beta.assistants.create(
        name="KeywordExtractor",
        instructions="Extract search keywords to JSON",
        model="gpt-4o",
    )

    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=input,
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    while run.status != "completed":
        time.sleep(2)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return messages.data[0].content[0].text.value

def mail_fetch(input):
    def decode_subject(subject):
        decoded = decode_header(subject)[0][0]
        return decoded.decode('utf-8') if isinstance(decoded, bytes) else decoded

    IMAP_SERVER = 'imap.gmail.com'
    EMAIL_ADDRESS = os.environ['Email']
    PASSWORD = os.environ['Password']

    mail = imaplib.IMAP4_SSL(IMAP_SERVER, 993)
    mail.login(EMAIL_ADDRESS, PASSWORD)
    mail.select('inbox')

    status, email_ids = mail.search(None, f'(OR BODY "{input}" FROM "{input}" SUBJECT "{input}")')
    
    if status == 'OK':
        for email_id in email_ids[0].split():
            status, email_data = mail.fetch(email_id, '(RFC822)')
            if status == 'OK':
                msg = email.message_from_bytes(email_data[0][1])
                print(f"""
                Subject: {decode_subject(msg['subject'])}
                From: {decode_subject(msg['from'])}
                Date: {msg['date']}
                """)
    
    mail.logout()

# FastAPI Application Setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class MessageIn(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"message": "Azure OpenAI Integrated Backend"}

@app.post("/transcript")
async def transcript(message_in: MessageIn):
    res = classify(message_in.message)
    steps = jsonSteps(message_in.message)

    print("classification res",res)
    
    if res == '4':
        devin_beta(message_in.message)
    
    return {
        "req": res,
        "steps": json.loads(steps) if res == '4' else None
    }

@app.post("/sendmail")
async def send_mail(message_in: MessageIn):
    mail_data = jsonBody(message_in.message)
    return {"mail_components": json.loads(mail_data)}

@app.post("/fetchmail")
async def fetch_mail(message_in: MessageIn):
    keyword_data = jsonKeyword(message_in.message)
    keyword = json.loads(keyword_data)["keyword"]
    mail_fetch(keyword)
    return {"status": f"Processed emails for keyword: {keyword}"}

@app.post("/upload_audio/")
async def upload_audio(audio_file: UploadFile = File(...)):
    return {"filename": audio_file.filename}

@app.get("/abort")
async def abort_process():
    return {"status": "Process terminated"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
