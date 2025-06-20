import os
from openai import AzureOpenAI
from dotenv import load_dotenv

def validate_azure_gpt4o():
    """Azure GPT-4o API validation"""
    print("hello")
    try:
        load_dotenv()

        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-05-01-preview",
            azure_endpoint=os.getenv("AZURE_ENDPOINT")
        )

        print("sending")
        test = client.chat.completions.create(
            model="gpt-4o",  # or "gpt-4o-2"
            messages=[{"role": "user", "content": "give me a html file which says rudresh pandey and green color background. no external css file all incoorporated in html only"}],
            max_tokens=100,
            timeout=None
        )
        print(test.choices[0].message.content)
        print("Response ID:", test.id)
        return True

    except Exception as e:
        print("Error:", e)
        return False

validate_azure_gpt4o()
