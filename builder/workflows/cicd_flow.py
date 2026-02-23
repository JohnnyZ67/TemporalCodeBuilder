from datetime import timedelta
from temporalio import workflow, activity
from typing import Optional
from dataclasses import dataclass
import logging

with workflow.unsafe.imports_passed_through():
    from builder.activities.git_acts import refresh_repo, check_for_changes
    from builder.activities.python_acts import install_packages, build_image, perform_tests
    from builder.activities.terraform_acts import terraform_plan, terraform_apply
    from builder.activities.utitily_acts import notify_users

@dataclass
class ApproveInput:
    name: str

@workflow.defn
class CicdWorkflow:

    def __init__(self) -> None:
        self.approved_for_release = False
        self.approver_name: Optional[str] = None

    @workflow.signal
    def approve(self, input: ApproveInput) -> None:
        self.approved_for_release = True
        self.approver_name = input.name

    @workflow.run
    async def run(self, input: dict) -> str:

        git_check = await workflow.execute_activity(
            check_for_changes,
            "",
            schedule_to_close_timeout=timedelta(minutes=10),
        )

        # This is set to True for testing to make sure we can see all stages run. Revert to git_check to avoid unneeded operations.
        if(True): #git_check['change_required']):

            commit_hash = await workflow.execute_activity(
                refresh_repo,
                git_check['clone_required'],
                schedule_to_close_timeout=timedelta(minutes=10),
            )
        
            await workflow.execute_activity(
                install_packages,
                schedule_to_close_timeout=timedelta(minutes=10),
            )

            test_results = await workflow.execute_activity(
                perform_tests,
                schedule_to_close_timeout=timedelta(minutes=30)
            )

            if(test_results['passed']):

                await workflow.execute_activity(
                    build_image,
                    schedule_to_close_timeout=timedelta(minutes=15)
                )

                await workflow.execute_activity(
                    terraform_plan,
                    schedule_to_close_timeout=timedelta(minutes=15)
                )

                if(not input['autodeploy']):
                    await workflow.wait_condition(lambda: self.approved_for_release, timeout=timedelta(minutes=10))

                await workflow.execute_activity(
                    terraform_apply,
                    "tfplan",
                    schedule_to_close_timeout=timedelta(minutes=15)
                )

                await workflow.execute_activity(
                    notify_users,
                    True,
                    schedule_to_close_timeout=timedelta(minutes=2)
                )

                return f"Build completed - Successfully deployed new API image."



            

        return f"Build completed - No new changes"
