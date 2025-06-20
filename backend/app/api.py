from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import re
import subprocess
from dotenv import load_dotenv
from openai import AzureOpenAI
from datetime import datetime
import time

load_dotenv()
app = FastAPI()

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

# Agent 1: Code Writer
def create_code_writer():
    return client.beta.assistants.create(
        name="Code Architect",
        instructions="Generate initial HTML/CSS/JS code based on user requirements. Focus on responsive design and core functionality.",
        model="gpt-4o",
        tools=[{"type": "code_interpreter"}]
    )

# Agent 2: Code Reviewer
def create_code_reviewer():
    return client.beta.assistants.create(
        name="Code Auditor",
        instructions="Analyze code for errors, security issues, and best practices. Check for:\n1. Syntax errors\n2. Accessibility issues\n3. Responsive design\n4. Browser compatibility\n5. Performance optimizations",
        model="gpt-4o"
    )

# Agent 3: Code Fixer
def create_code_fixer():
    return client.beta.assistants.create(
        name="Code Surgeon",
        instructions="Fix identified issues while preserving original functionality. Implement reviewer suggestions and verify corrections.",
        model="gpt-4o",
        tools=[{"type": "code_interpreter"}]
    )

def process_code_response(response: str):
    try:
        html_match = re.search(r'```html\n(.*?)\n```', response, re.DOTALL)
        return html_match.group(1).strip() if html_match else response
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Code processing failed: {str(e)}")

def collaborative_coding_flow(user_prompt: str):
    # Initialize agents
    writer = create_code_writer()
    reviewer = create_code_reviewer()
    fixer = create_code_fixer()

    # Phase 1: Initial Code Generation
    writer_thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=writer_thread.id,
        role="user",
        content=f"{user_prompt}\n\nOutput only the complete HTML/CSS/JS code in a single file."
    )

    writer_run = client.beta.threads.runs.create(
        thread_id=writer_thread.id,
        assistant_id=writer.id
    )

    # Wait for initial code generation
    while writer_run.status not in ["completed", "failed"]:
        time.sleep(5)
        writer_run = client.beta.threads.runs.retrieve(
            thread_id=writer_thread.id,
            run_id=writer_run.id
        )

    if writer_run.status == "failed":
        raise HTTPException(status_code=500, detail="Initial code generation failed")

    # Get generated code
    messages = client.beta.threads.messages.list(writer_thread.id)
    initial_code = process_code_response(messages.data[0].content[0].text.value)

    # Phase 2: Code Review
    review_thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=review_thread.id,
        role="user",
        content=f"Review this code:\n{initial_code}\n\nIdentify issues and suggest improvements."
    )

    review_run = client.beta.threads.runs.create(
        thread_id=review_thread.id,
        assistant_id=reviewer.id
    )

    # Wait for code review
    while review_run.status not in ["completed", "failed"]:
        time.sleep(5)
        review_run = client.beta.threads.runs.retrieve(
            thread_id=review_thread.id,
            run_id=review_run.id
        )

    if review_run.status == "failed":
        return initial_code  # Return original code if review fails

    # Get review feedback
    review_messages = client.beta.threads.messages.list(review_thread.id)
    review_feedback = review_messages.data[0].content[0].text.value

    # Phase 3: Code Correction
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

    # Wait for code fixes
    while fix_run.status not in ["completed", "failed"]:
        time.sleep(5)
        fix_run = client.beta.threads.runs.retrieve(
            thread_id=fix_thread.id,
            run_id=fix_run.id
        )

    if fix_run.status == "failed":
        return initial_code  # Return original code if correction fails

    # Get final code
    fix_messages = client.beta.threads.messages.list(fix_thread.id)
    final_code = process_code_response(fix_messages.data[0].content[0].text.value)

    return final_code

@app.post("/create-project")
async def create_project(request: MessageIn):
    try:
        final_code = collaborative_coding_flow(request.message)
        
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
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/deploy")
async def deploy_project(request: DeployRequest):
    try:
        project_path = os.path.join("projects", request.project_dir)
        
        # Save final validated code
        with open(os.path.join(project_path, "index.html"), "w") as f:
            f.write(request.code)

        # Deploy using Vercel CLI
        result = subprocess.run(
            ["npx", "vercel", "--yes"],
            cwd=project_path,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(f"Deployment failed: {result.stderr}")

        # Extract deployment URL
        url_match = re.search(r'https://.*?\.vercel\.app', result.stdout)
        deployment_url = url_match.group(0) if url_match else None

        return {
            "status": "deployed",
            "deployment_url": deployment_url,
            "project_dir": request.project_dir
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
