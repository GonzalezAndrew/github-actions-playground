import anyio
import sys
import dagger
import os

async def main():
    APPLY = os.environ["APPLY", True]
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:

        terraform_dir = client.host().directory("./terraform")
        docker_host = client.host().unix_socket("/var/run/docker.sock")

        builder = (
            client.container()
            .build(context=terraform_dir)
            .with_unix_socket("/var/run/docker.sock", docker_host)
            .with_mounted_directory("/src", terraform_dir)
            .with_workdir("/src")
        )

        terraform_init = (
            builder
            .exec(["terraform", "init"])
        )
        
        terraform_plan = (
            terraform_init
            .exec(["terraform", "plan"])
        )

        if APPLY:
            terraform_apply = await (
                terraform_plan
                .exec(["terraform", "apply", "-input=false", "-auto-approve"])
            ).exit_code()
        else:
            await terraform_plan.exit_code()

anyio.run(main)