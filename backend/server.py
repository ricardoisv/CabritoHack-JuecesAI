from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from main import evaluate_project
import uvicorn
import traceback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Project(BaseModel):
    name: str
    description: str

class EvaluationResult(BaseModel):
    result: str

@app.post("/evaluate", response_model=EvaluationResult)
async def evaluate(project: Project):
    try:
        project_description = f"Project name: {project.name}\n\nDescription: {project.description}"
        result = evaluate_project(project_description)
        return EvaluationResult(result=result)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to the Hackathon Judging API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)