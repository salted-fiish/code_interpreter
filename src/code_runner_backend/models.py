from pydantic import BaseModel

class CodePrompt(BaseModel):
    prompt: str
