import os
from openai import OpenAI

from keys.config import OPENAI_API_KEY
# Google Docs fetcher not needed here - handled by caller

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)
    
def generate_ai_response(prompt, context) -> str:
    try:
        
        # Convert context dict to structured text
        context_str = ""
        if isinstance(context, dict):
            for key, value in context.items():
                context_str += f"{key.title().replace('_', ' ')}: {value}\n\n"
        else:
            context_str = str(context)
        
        # Combine prompt and context into a single system message
        combined_prompt = f"{prompt}\n\n{context_str.strip()}"
        
        messages = [
            {"role": "system", "content": combined_prompt}
        ]
        
        # Use GPT-5 as specified
        model = "gpt-5"
        max_tokens = 8000
        
        api_params = {
            "model": model,
            "messages": messages,
            "max_completion_tokens": max_tokens
        }
        
        response = client.chat.completions.create(**api_params)
        ai_response = response.choices[0].message.content
        
        return ai_response
        
    except Exception as e:
        # Log the actual error for debugging
        print(f"Error generating AI response: {str(e)}")
        return f"I apologize, but I encountered an error: {str(e)}. Please try again."