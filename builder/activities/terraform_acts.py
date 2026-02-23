from temporalio import activity
import subprocess
import shutil
import os

PROJECT_PATH = "example/api/repo"

@activity.defn
async def terraform_plan() -> str:
    tflocal_bin = shutil.which("tflocal") or "tflocal"

    # Create TF plan at tfplan for apply step
    subprocess.run([tflocal_bin, 'init'], cwd=f"{os.getcwd()}/{PROJECT_PATH}/provisioning", capture_output=True)
    subprocess.run([tflocal_bin, 'plan', '-out=tfplan'], cwd=f"{os.getcwd()}/{PROJECT_PATH}/provisioning", capture_output=True)

    return "Terraform Plan complete. Waiting for approval."

@activity.defn
async def terraform_apply(tf_plan: str) -> str:
    tflocal_bin = shutil.which("tflocal") or "tflocal"
    subprocess.run([tflocal_bin, 'apply', 'tfplan'], cwd=f"{os.getcwd()}/{PROJECT_PATH}/provisioning", capture_output=True)
    return "terraform apply complete"