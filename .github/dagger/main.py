"""
Run tests for multiple Python versions concurrently.
"""

import sys

import anyio
import dagger


async def test():
    versions = ["3.7", "3.8", "3.9", "3.10", "3.11"]

    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:

        async def test_version(version: str):
            python = (
                client.container().from_(f"python:{version}-slim-buster")
                # ouptut Python Version
                .with_exec(["python", "-V"])
            )

            print(f"Starting tests for Python {version}")

            # execute
            await python.exit_code()

            print(f"Tests for Python {version} succeeded!")

        # when this block exits, all tasks will be awaited (i.e., executed)
        async with anyio.create_task_group() as tg:
            for version in versions:
                tg.start_soon(test_version, version)

    print("All tasks have finished")


async def build():
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:
        python = client.container().build(client.host().directory(f"./service_1"))

        image = await python.publish("ttl.sh/footestdagger:5m")

    print(f"Image has been pushed {image}")


async def terraform_run():
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:
        terraform_dir = client.host().directory("./terraform")

        terraform_plan = (
            client.container()
            .from_("hashicorp/terraform:1.3.1")
            .with_mounted_directory("/src", terraform_dir)
            .with_workdir("/src")
            .exec(["init"])
            .exec(["plan", "-input=false", "-out=tfplan"])
            .exec(["show", "-json", "tfplan"])
        )
        exit_code = await terraform_plan.exit_code()
        print(exit_code)

    return terraform_plan.directory("/output")


if __name__ == "__main__":
    anyio.run(terraform_run)
