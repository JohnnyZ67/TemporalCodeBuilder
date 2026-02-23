from temporalio import activity
from git import Repo
import os

PROJECT_PATH = "example/api/repo"
PROJECT_REPO_URL = "https://github.com/JohnnyZ67/TotallyRealApplication.git"

@activity.defn
async def check_for_changes(current_commit_hash: str) -> dict:
    try:
        repo = Repo(PROJECT_PATH) 
        repo.remotes.origin.fetch()

        # Get local and remote commit hashes
        branch = repo.active_branch
        local_commit = repo.commit(branch.name).hexsha
        remote_commit = repo.commit(f"origin/{branch.name}").hexsha

        print(f"Local  ({branch.name}): {local_commit}")
        print(f"Origin ({branch.name}): {remote_commit}")
       
        return {
            "change_required": local_commit != remote_commit,
            "clone_required": False
        }
    except Exception as e:
        print("Catching exception")
        print(e)
        return {
            "change_required": True,
            "clone_required": True
        }

@activity.defn
async def refresh_repo(clone_required: bool) -> str:
    # Using public repositories so this is simpler, but in the real world there would be extra pieces for authentication and secrets management so leaving as a separate activity
    
    if(clone_required):
        print(f"Starting clone from {PROJECT_REPO_URL}")
        repo = Repo.clone_from(PROJECT_REPO_URL, PROJECT_PATH)
        print(f"Cloned repository from {PROJECT_REPO_URL}")
    else:
        print("Fetching and merging app updates")
        repo = Repo(PROJECT_PATH)
        repo.remotes.origin.pull()
        print("Merge complete.")

    return "Repo updated successfully"
