"""
Run tests for multiple Python versions concurrently.
"""

import sys
import anyio
import dagger

from pathlib import Path

def find_repo_path(path: str = __file__) -> str:
    """Find the root path of the repository and return it.
    :param path: The path where we should be looking.
    :return: The root path of the repository.
    :rtype: str
    """
    for path in Path(path).parents:
        # Check whether "path/.git" exists and is a directory
        git_dir = path / ".git"
        if git_dir.is_dir():
            return path.as_posix()


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
    repo_path = find_repo_path()
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:
        python = client.container().build(client.host().directory(f"{repo_path}/service_1/"))

        image = await python.publish("ttl.sh/footestdagger:5m")

    print(f"Image has been pushed {image}")


if __name__ == "__main__":
    anyio.run(build)
