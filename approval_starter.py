import asyncio
import uuid
from typing import Optional
from temporalio.client import Client
from temporalio.envconfig import ClientConfig
from builder.workflows.cicd_flow import CicdWorkflow

async def main(client: Optional[Client] = None):
    if not client:
        config = ClientConfig.load_client_connect_config()
        config.setdefault("target_host", "localhost:7233")
        client = await Client.connect(**config)
    
    result = await client.start_workflow(
        CicdWorkflow.run,
        {"name": "cicd-workflow", "autodeploy": False},
        id=f"total-build-{uuid.uuid4()}",
        task_queue="cicd-queue",
    )
    print("Workflow result:", result)

if __name__ == "__main__":
    asyncio.run(main())