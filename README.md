# 🚀 Breeze Pro — Build, Preview, and Deploy with AI

Breeze Pro is a multi-agent AI-powered project builder that lets you describe your idea, see it coded live in a sandbox, iterate through AI suggestions or your own edits, and deploy instantly — all in one interface.

![Breeze Pro Demo](./Screenshot%202025-06-21%20at%201.52.59%20AM.png)

## ✨ Features

- 🧠 **Multi-agent AI assistant** to understand requirements, break them into tasks, and write code.
- ⚡ **Live code sandbox** with real-time preview and editing.
- 🔁 **User in-chat feedback** to iteratively refine your project.
- ☁️ **One-click Vercel deployment** with shareable URL.
- 📦 Supports full-stack apps and instant prototyping.

---

## 🛠️ Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/breeze-pro.git
cd breeze-pro
```

### 2. Install dependencies
```bash
npm install
```

### 3. Configure Environment Variables  
Create a `.env` file in the root directory with the following:
```env
AZURE_OPENAI_KEY=your_azure_openai_key
AZURE_ENDPOINT=your_azure_endpoint_url
```

### 4. Run Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
python main.py
```

### 5. Run Frontend
Open another terminal:
```bash
npm run dev
```

---

## 🧪 Example Use Case

1. Describe a project like:  
   > *"Make me a snake game that eats and gets big with walls on all four sides"*

2. Watch the AI write and display the code in the editor + live preview.

3. Click `Request Changes` or type:  
   > *"Add score counter"*

4. Hit **Deploy**, and you're done! 🎯

![Live Code Sandbox](./Screenshot%202025-06-21%20at%201.52.18%20AM.png)

---

## 📎 Deployment

Breeze Pro uses Vercel for seamless one-click deployment. Just click **Deploy**, and your project will be published with a live link you can share.

---

## 🧩 Tech Stack

- Frontend: React, TailwindCSS  
- Backend: FastAPI, LangChain, Azure OpenAI  
- Deployment: Vercel  
- Agents: Role-based multi-agent system

---

## 📸 UI Overview

![Start New Project](./Screenshot%202025-06-21%20at%201.49.14%20AM.png)

---

## 🤖 Powered By

- Azure OpenAI  
- LangChain  
- Vercel  
- You 🫵
