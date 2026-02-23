import asyncio
from temporalio.client import Client
from temporalio.envconfig import ClientConfig
from temporalio.worker import Worker
from temporalio import workflow


with workflow.unsafe.imports_passed_through():
    from builder.workflows.cicd_flow import CicdWorkflow
    from builder.activities.git_acts import refresh_repo, check_for_changes
    from builder.activities.python_acts import install_packages, build_image, perform_tests
    from builder.activities.terraform_acts import terraform_plan, terraform_apply
    from builder.activities.utitily_acts import notify_users


async def main():
    config = ClientConfig.load_client_connect_config()
    config.setdefault("target_host", "localhost:7233")
    client = await Client.connect(**config)
    
    worker = Worker(
        client,
        task_queue="cicd-queue",
        workflows=[CicdWorkflow],
        activities=[
            check_for_changes,
            refresh_repo,
            install_packages,
            build_image,
            perform_tests,
            terraform_plan,
            terraform_apply,
            notify_users
        ]
    )
    print("Cicd worker started.")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())