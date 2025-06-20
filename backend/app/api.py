from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import re
import subprocess
from dotenv import load_dotenv
from openai import AzureOpenAI
from datetime import datetime
import time
import logging
import shutil

load_dotenv()
app = FastAPI()
logging.basicConfig(level=logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-05-01-preview",
    azure_endpoint=os.getenv("AZURE_ENDPOINT")
)

# ... (Keep previous BaseModel definitions)

# Configuration
load_dotenv()
app = FastAPI()
logging.basicConfig(level=logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-05-01-preview",
    azure_endpoint=os.getenv("AZURE_ENDPOINT")
)

class MessageIn(BaseModel):
    message: str

class DeployRequest(BaseModel):
    code: str
    project_dir: str

class UpdateRequest(BaseModel):
    project_dir: str
    code: str
    message: str

# Agent Management
def create_agent(name, instructions):
    logging.info(f"Initializing {name} agent...")
    return client.beta.assistants.create(
        name=name,
        instructions=instructions,
        model="gpt-4o",
        tools=[{"type": "code_interpreter"}]
    )

def log_agent_action(agent_name: str, action: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"[{timestamp}] {agent_name} {action}")

# Agent Definitions
WRITER_INSTRUCTIONS = """Generate HTML/CSS/JS code based on requirements. Follow:
1. Mobile-first responsive design
2. Semantic HTML5
3. Modern CSS (Flexbox/Grid)
4. ES6+ JavaScript
5. Accessibility features"""

REVIEWER_INSTRUCTIONS = """Analyze code for:
1. Syntax errors
2. Security vulnerabilities
3. Performance issues
4. Accessibility (a11y) compliance
5. Cross-browser compatibility
6. Responsive design breakpoints"""

FIXER_INSTRUCTIONS = """Correct identified issues while:
1. Preserving original functionality
2. Maintaining code style consistency
3. Adding documentation comments
4. Implementing fallbacks for unsupported features"""

class ImageUploadRequest(BaseModel):
    project_dir: str

def process_ai_response(response: str):
    try:
        html_match = re.search(r'```html\n(.*?)\n```', response, re.DOTALL)
        return html_match.group(1).strip() if html_match else response
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Code processing failed: {str(e)}")

def execute_agent_workflow(prompt: str, existing_code: str = None):
    log_agent_action("System", "Starting collaborative coding workflow")
    
    # Initialize agents
    writer = create_agent("Code Architect", WRITER_INSTRUCTIONS)
    reviewer = create_agent("Code Auditor", REVIEWER_INSTRUCTIONS)
    fixer = create_agent("Code Surgeon", FIXER_INSTRUCTIONS)

    # Phase 1: Code Generation/Modification
    log_agent_action("Code Writer", "Generating initial implementation")
    writer_thread = client.beta.threads.create()
    base_prompt = f"{prompt}\n\nOutput only the complete HTML/CSS/JS code in a single file."
    if existing_code:
        base_prompt = f"Modify this code:\n{existing_code}\n\nNew requirements: {prompt}"

    client.beta.threads.messages.create(
        thread_id=writer_thread.id,
        role="user",
        content=base_prompt
    )

    writer_run = client.beta.threads.runs.create(
        thread_id=writer_thread.id,
        assistant_id=writer.id
    )

    while writer_run.status not in ["completed", "failed"]:
        time.sleep(3)
        writer_run = client.beta.threads.runs.retrieve(
            thread_id=writer_thread.id,
            run_id=writer_run.id
        )

    if writer_run.status == "failed":
        raise HTTPException(status_code=500, detail="Initial code generation failed")

    initial_code = process_ai_response(
        client.beta.threads.messages.list(writer_thread.id).data[0].content[0].text.value
    )

    # Phase 2: Code Review
    log_agent_action("Code Reviewer", "Analyzing code quality")
    review_thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=review_thread.id,
        role="user",
        content=f"Review this code:\n{initial_code}"
    )

    review_run = client.beta.threads.runs.create(
        thread_id=review_thread.id,
        assistant_id=reviewer.id
    )

    while review_run.status not in ["completed", "failed"]:
        time.sleep(3)
        review_run = client.beta.threads.runs.retrieve(
            thread_id=review_thread.id,
            run_id=review_run.id
        )

    review_feedback = ""
    if review_run.status == "completed":
        review_feedback = client.beta.threads.messages.list(review_thread.id).data[0].content[0].text.value

    # Phase 3: Code Correction
    log_agent_action("Code Fixer", "Implementing improvements")
    fix_thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=fix_thread.id,
        role="user",
        content=f"Original code:\n{initial_code}\n\nReview feedback:\n{review_feedback}\n\nProvide corrected code."
    )

    fix_run = client.beta.threads.runs.create(
        thread_id=fix_thread.id,
        assistant_id=fixer.id
    )

    while fix_run.status not in ["completed", "failed"]:
        time.sleep(3)
        fix_run = client.beta.threads.runs.retrieve(
            thread_id=fix_thread.id,
            run_id=fix_run.id
        )

    final_code = initial_code
    if fix_run.status == "completed":
        final_code = process_ai_response(
            client.beta.threads.messages.list(fix_thread.id).data[0].content[0].text.value
        )

    return final_code

@app.post("/create-project")
async def create_project(request: MessageIn):
    try:
        final_code = execute_agent_workflow(request.message)
        
        project_dir = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_path = os.path.join("projects", project_dir)
        os.makedirs(project_path, exist_ok=True)

        with open(os.path.join(project_path, "index.html"), "w") as f:
            f.write(final_code)

        return {
            "project_dir": project_dir,
            "code": final_code,
            "status": "draft"
        }

    except Exception as e:
        log_agent_action("System", f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update-project")
async def update_project(request: UpdateRequest):
    try:
        log_agent_action("System", f"Processing change request: {request.message[:50]}...")
        final_code = execute_agent_workflow(
            request.message,
            existing_code=request.code
        )
        
        project_path = os.path.join("projects", request.project_dir)
        with open(os.path.join(project_path, "index.html"), "w") as f:
            f.write(final_code)

        return {
            "code": final_code,
            "project_dir": request.project_dir
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/upload-image")
async def upload_image(
    project_dir: str,
    file: UploadFile = File(...)
):
    try:
        project_path = os.path.join("projects", project_dir)
        assets_path = os.path.join(project_path, "assets")
        os.makedirs(assets_path, exist_ok=True)
        
        file_path = os.path.join(assets_path, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {"filename": file.filename, "path": f"assets/{file.filename}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ... (Keep previous endpoints)

@app.post("/deploy")
async def deploy_project(request: DeployRequest):
    try:
        project_path = os.path.join("projects", request.project_dir)
        
        # Write code and preserve assets
        with open(os.path.join(project_path, "index.html"), "w") as f:
            f.write(request.code)

        # Deploy entire project directory
        result = subprocess.run(
            ["npx", "vercel", "--yes"],
            cwd=project_path,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(f"Deployment failed: {result.stderr}")

        url_match = re.search(r'https://.*?\.vercel\.app', result.stdout)
        return {
            "status": "deployed",
            "deployment_url": url_match.group(0) if url_match else None,
            "project_dir": request.project_dir
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @app.post("/deploy")
# async def deploy_project(request: DeployRequest):
#     try:
#         project_path = os.path.join("projects", request.project_dir)
        
#         with open(os.path.join(project_path, "index.html"), "w") as f:
#             f.write(request.code)

#         result = subprocess.run(
#             ["npx", "vercel", "--yes"],
#             cwd=project_path,
#             capture_output=True,
#             text=True
#         )

#         if result.returncode != 0:
#             raise Exception(f"Deployment failed: {result.stderr}")

#         url_match = re.search(r'https://.*?\.vercel\.app', result.stdout)
#         return {
#             "status": "deployed",
#             "deployment_url": url_match.group(0) if url_match else None,
#             "project_dir": request.project_dir
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
