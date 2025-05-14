import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from code_runner_backend.logs import logger_instance

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Please set the OPENAI_API_KEY environment variable")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """You are a Python code generation assistant. Please follow these rules:

1. Maintain conversation coherence and understand user's context
2. If the user's request is unclear, proactively ask for clarification
3. Output format:
   - First explain your approach and implementation method in English
   - Then wrap the Python code in triple backticks
   - Finally, add some usage instructions
4. Code should be concise, efficient, and include necessary comments
5. If the user requests modifications to previous code, improve based on the existing code
6. If the user's request is related to previous code, reference the previous implementation
7. If code execution fails, analyze the error and provide a fix

Remember: Maintain conversation coherence, understand context, provide clear explanations and high-quality code."""

async def generate_code(prompt: str, history: list = None, error: str = None) -> dict:
    try:
        # Build message list
        messages = []
        
        # Add system prompt only for first conversation
        if not history:
            messages.append({"role": "system", "content": SYSTEM_PROMPT})
        else:
            # Use conversation history, but remove previous system prompts
            messages = [msg for msg in history if msg["role"] != "system"]
            # Ensure first message is system prompt
            messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
        
        # Add error information if present
        if error:
            prompt = f"Code execution error: {error}\nPlease fix this issue: {prompt}"
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        # Log messages sent to GPT
        logger_instance.info("Messages sent to GPT:")
        for msg in messages:
            logger_instance.info(f"{msg['role']}: {msg['content']}")
        
        # Call GPT
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.3
        )
        
        # Get GPT's response
        content = response.choices[0].message.content.strip()
        
        # Log GPT's response
        logger_instance.info(f"GPT's response:\n{content}")
        
        # Extract code section
        code = ""
        if "```python" in content:
            code = content.split("```python")[1].split("```")[0].strip()
            logger_instance.info(f"Extracted code:\n{code}")
        
        # Update conversation history
        new_history = messages + [{"role": "assistant", "content": content}]
        
        return {
            "explanation": content,
            "code": code,
            "gpt_log": {
                "messages": messages,
                "response": content
            },
            "history": new_history
        }
    except Exception as e:
        logger_instance.error(f"Error generating code: {str(e)}")
        raise Exception(f"Code generation failed: {str(e)}")
