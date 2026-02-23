import asyncio
import uuid
from typing import Optional
from datetime import timedelta
from temporalio.client import (
    Client,
    Schedule,
    ScheduleActionStartWorkflow,
    ScheduleIntervalSpec,
    ScheduleSpec,
    ScheduleState,
)
from temporalio.envconfig import ClientConfig
from builder.workflows.cicd_flow import CicdWorkflow

async def main(client: Optional[Client] = None):
    if not client:
        config = ClientConfig.load_client_connect_config()
        config.setdefault("target_host", "localhost:7233")
        client = await Client.connect(**config)
    
    await client.create_schedule(
        "cicd-auto-deployer-schedule",
        Schedule(
            action=ScheduleActionStartWorkflow(
                CicdWorkflow.run,
                {"name": "cicd-workflow", "autodeploy": True},
                id=f"total-build-auto-{uuid.uuid4()}",
                task_queue="cicd-queue",
            ),
            spec=ScheduleSpec(
                intervals=[ScheduleIntervalSpec(every=timedelta(minutes=5))]
            ),
            state=ScheduleState(note="Detecting and deploying any code changes on repository"),
        ),
    )

    print("Schedule added for auto code deployer")

if __name__ == "__main__":
    asyncio.run(main())