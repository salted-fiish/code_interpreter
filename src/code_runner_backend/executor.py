import sys
from io import StringIO
import traceback
from code_runner_backend.logs import logger_instance

def run_code(code: str) -> dict:
    try:
        # Capture standard output and error output
        stdout = StringIO()
        stderr = StringIO()
        sys.stdout = stdout
        sys.stderr = stderr
        
        # Create a new namespace
        namespace = {}
        
        # Execute code
        exec(code, namespace)
        
        # Restore standard output and error output
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        
        # Get output
        output = stdout.getvalue()
        error = stderr.getvalue()
        
        if error:
            return {
                "status": "error",
                "output": error
            }
        else:
            return {
                "status": "success",
                "output": output
            }
    except Exception as e:
        error_msg = f"Execution error: {str(e)}"
        logger_instance.error(error_msg)
        return {
            "status": "error",
            "output": error_msg
        }
