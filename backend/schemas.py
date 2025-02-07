from pydantic import BaseModel

class GitHubActivity(BaseModel):
    date: str
    commits: int