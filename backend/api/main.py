from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import time
import subprocess
import re
from dotenv import load_dotenv
from openai import AzureOpenAI
from datetime import datetime

# Configuration
load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Azure Client Setup
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

# Core Workflow Functions
def generate_project_structure(response: str) -> str:
    """Extract HTML/CSS/JS from AI response with validation"""
    try:
        html_match = re.search(r'```html\n(.*?)\n```', response, re.DOTALL)
        css_match = re.search(r'```css\n(.*?)\n```', response, re.DOTALL)
        
        html_content = html_match.group(1) if html_match else ""
        css_content = css_match.group(1) if css_match else ""

        # Validate basic HTML structure
        if not html_content.strip().startswith("<!DOCTYPE html>"):
            html_content = f"<!DOCTYPE html>\n<html>\n{html_content}\n</html>"

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>{css_content}</style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Code extraction failed: {str(e)}")

def deploy_to_vercel(project_path: str):
    """Handle deployment process with proper error handling"""
    try:
        os.chdir(project_path)
        result = subprocess.run(
            ["npx", "vercel", "--yes"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Deployment failed: {e.stderr}")

# Main Workflow Endpoints
@app.post("/create-project")
async def create_project_endpoint(request: MessageIn):
    try:
        # Generate code with Azure OpenAI
        assistant = client.beta.assistants.create(
            name="Portfolio Generator",
            instructions="Create responsive portfolio with embedded CSS/JS",
            model="gpt-4o",
        )

        thread = client.beta.threads.create()
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"{request.message} Include all code in single HTML file with embedded CSS/JS",
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        # Wait for completion
        while run.status not in ["completed", "failed"]:
            time.sleep(5)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

        if run.status == "failed":
            raise HTTPException(status_code=500, detail="AI generation failed")

        # Process response
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        ai_response = messages.data[0].content[0].text.value
        
        # Create project structure
        project_dir = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_path = os.path.join(os.getcwd(), "projects", project_dir)
        os.makedirs(base_path, exist_ok=True)
        
        full_code = generate_project_structure(ai_response)

        # Save initial version (not deployed yet)
        with open(os.path.join(base_path, "index.html"), "w") as f:
            f.write(full_code)

        return {
            "status": "draft",
            "project_dir": project_dir,
            "code": full_code,
            "deployment_url": None
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def deploy_to_vercel(project_path: str):
    """Handle Vercel deployment with proper terminal interaction"""
    try:
        os.chdir(project_path)
        
        # 1. Initialize Vercel project if not exists
        if not os.path.exists(os.path.join(project_path, 'vercel.json')):
            subprocess.run(
                ["npx", "vercel", "init", "--yes"],
                check=True,
                capture_output=True,
                text=True
            )

        # 2. Full deployment process
        result = subprocess.run(
            ["npx", "vercel", "deploy", "--prod", "--yes"],
            capture_output=True,
            text=True,
            check=True,
            timeout=120  # 2 minute timeout
        )
        
        # 3. Extract deployment URL
        url_match = re.search(r'Production: (https://.*?\.vercel\.app)', result.stdout)
        if not url_match:
            raise RuntimeError("Could not extract deployment URL")
            
        return {
            "url": url_match.group(1),
            "logs": result.stdout
        }

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Deployment timed out")
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Deployment failed: {e.stderr}\n\n{e.stdout}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
