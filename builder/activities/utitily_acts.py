from temporalio import activity

@activity.defn
async def notify_users(successful_build: bool) -> str:
    return "notifying_slack/teams/whatever"