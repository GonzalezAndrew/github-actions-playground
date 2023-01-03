import sys

import anyio
import dagger
from dagger.api.gen import Container

terraform_work_dir = "./terraform"


def terraform_image(
    client: dagger.Client, mounted_dir: dagger.Directory
):
    """Builds and returns the base terraform image as a dagger container object.
    :param client: The dagger client that will be used.
    :param mounted_dir: The directory where the Terraform config files are located.
    :return: A dagger container object.
    :rtype: dagger.Client.Container
    """

    docker_host = client.host().unix_socket("/var/run/docker.sock")
    base_image = (
        client.container()
        .build(context=mounted_dir)
        .with_unix_socket("/var/run/docker.sock", docker_host)
        .with_mounted_directory("/src", mounted_dir)
        .with_workdir("/src")
    )
    return base_image

def terraform_init(
    base: dagger.Container, client: dagger.Client, mounted_dir: dagger.Directory
) -> dagger.Directory:
    """Runs a terraform init.
    :param base: The base terraform image.
    :return: The exit code from the terraform init.
    :rtype: int
    """

    terraform_init = base.exec(["terraform", "init", "-input=false"])
    outputs = client.directory()
    return outputs.with_directory("/", terraform_init.directory("/src"))
    


def terraform_plan(
    base: dagger.Container, client: dagger.Client, mounted_dir: dagger.Directory
) -> dagger.Directory:
    terraform_plan = (
        base
        .exec(["terraform", "plan", "-input=false"])
    )

    outputs = client.directory()
    return outputs.with_directory("/", terraform_plan.directory("/src"))


async def main():
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:
        terraform_dir = client.host().directory(terraform_work_dir)

        terraform_base_image = terraform_image(client, mounted_dir=terraform_dir)
        
        init_output = terraform_init(base=terraform_base_image, client=client, mounted_dir=terraform_dir)
        plan_output = terraform_plan(base=terraform_base_image, client=client, mounted_dir=init_output)
        
        out = await plan_output.entries()
        print(out)
        

        
        
        #output = await terraform_init(terraform_base_image, client, terraform_dir)

    print("done")


if __name__ == "__main__":
    anyio.run(main)
