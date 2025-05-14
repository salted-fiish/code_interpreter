from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from code_runner_backend.executor import run_code
from code_runner_backend.gpt_client import generate_code
from code_runner_backend.logs import logger_instance
import json

router = APIRouter()

@router.post("/run_code")
async def run_code_from_prompt(prompt: str = Form(...), history: str = Form(None), error: str = Form(None)):
    logger_instance.info(f"Received prompt: {prompt}")
    if error:
        logger_instance.info(f"Received error: {error}")
    
    try:
        # Parse conversation history
        history_list = None
        if history:
            try:
                history_list = json.loads(history)
                logger_instance.info(f"Loaded history with {len(history_list)} messages")
            except json.JSONDecodeError:
                logger_instance.warning("Failed to parse history, starting new conversation")
        
        # Generate code and explanation
        result = await generate_code(prompt, history_list, error)
        explanation = result["explanation"]
        code = result["code"]
        gpt_log = result["gpt_log"]
        new_history = result["history"]
        
        # Log conversation
        logger_instance.info("=== GPT Conversation Log ===")
        for msg in gpt_log["messages"]:
            logger_instance.info(f"{msg['role']}: {msg['content']}")
        logger_instance.info(f"GPT Response: {gpt_log['response']}")
        logger_instance.info("=== Code Execution ===")
        logger_instance.info(f"Extracted code:\n{code}")
        
        # Execute code
        execution_result = run_code(code)
        
        # Combine results
        response = {
            "status": execution_result["status"],
            "explanation": explanation,
            "code": code,
            "output": execution_result["output"],
            "gpt_log": gpt_log,
            "history": new_history
        }
            
        return JSONResponse(content=response)
    except Exception as e:
        logger_instance.error(f"Error: {str(e)}")
        return JSONResponse(status_code=500, content={
            "status": "error",
            "output": str(e)
        })
