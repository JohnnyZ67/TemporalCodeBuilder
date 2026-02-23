from temporalio import activity
import pytest
import subprocess
import sys
import os

PROJECT_PATH = "example/api/repo"

@activity.defn
async def build_image() -> dict:
    result = subprocess.run(['docker', 'build', '-t', 'test_api:latest', '--build-arg', f"SRC_DIR={PROJECT_PATH}/src", '-f', f"{PROJECT_PATH}/Dockerfile", "."], capture_output=True)
    image_sha = subprocess.run(['docker', 'inspect', "--format='{{index .RepoDigests 0}}'", 'test_api:latest'], capture_output=True).stdout.decode('UTF-8')

    if(result.returncode == 0):

        # Commenting out but this would be needed for container registry use as we build our pipeline
        # tag_image = subprocess.call(['docker', 'tag', 'test_api:latest', 'example.container.registry.com/repo:latest'])
        # push_image = subprocess.call(['docker', 'push', 'example.container.registry.com/repo:latest'])

        return {
            "successful": True,
            "image_sha": image_sha
        }
    else:
        print("Build failed")
        return {
            "successful": False,
            "image_sha": ""
        }

@activity.defn
async def install_packages() -> str:
    subprocess.call([sys.executable, '-m', 'pip', 'install', '-r', f"{PROJECT_PATH}/requirements.txt"])


@activity.defn
async def perform_tests() -> dict:
    pytest.main(["-x", f"{PROJECT_PATH}/src"])

    return {"passed": True}
