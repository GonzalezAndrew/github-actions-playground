import sys

import anyio
import dagger
from dagger.api.gen import Container


async def terraform_image(
    client: dagger.Client, mounted_dir: dagger.Directory
) -> Container:
    """Builds and returns the base terraform image as a dagger container object.
    :param client: The dagger client that will be used.
    :param mounted_dir: The directory where the Terraform config files are located.
    :return: A dagger container object.
    :rtype: dagger.Client.Container
    """
    return (
        client.container()
        .from_("hashicorp/terraform:1.3.1")
        .with_mounted_directory("/src", mounted_dir)
        .with_workdir("/src")
    )


async def terraform_init(base: dagger.Container) -> int:
    """Runs a terraform init.
    :param base: The base terraform image.
    :return: The exit code from the terraform init.
    :rtype: int
    """
    # todo how to handle initalizing backend
    terraform_init = base.exec(["init"])

    init_exit_code = await terraform_init.exit_code()

    if init_exit_code == 0:
        return 0
    else:
        return 1


async def terraform_plan(base: dagger.Container) -> int:
    """Runs a terraform plan.
    :param base: The base terraform image.
    :return: The exit code from the terraform plan.
    :rtype: int
    """
    terraform_plan = base.exec(["plan", "-input=false", "-var-file=./inputs.tfvars"])

    plan_exit_code = await terraform_plan.exit_code()

    if plan_exit_code == 0:
        return 0
    else:
        return 1


async def terraform_apply(base: dagger.Container) -> int:
    """Runs a terraform apply.
    :param base: The base terraform image.
    :return: The exit code from the terraform apply.
    :rtype: int
    """
    terraform_apply = base.exec(["apply", "-auto-approve", "-input=false"])

    apply_exit_code = await terraform_apply.exit_code()

    if apply_exit_code == 0:
        return 0
    else:
        return 1


async def main():
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:
        terraform_dir = client.host().directory("./terraform")
        terraform_base_image = await terraform_image(client, mounted_dir=terraform_dir)

        tf_init_exit_code = await terraform_init(base=terraform_base_image)
        if tf_init_exit_code != 0:
            raise Exception("Terraform init failed!")

        tf_plan_exit_code = await terraform_plan(base=terraform_base_image)
        if tf_plan_exit_code != 0:
            raise Exception("Terraform plan failed!")

        tf_apply_exit_code = await terraform_apply(base=terraform_base_image)
        if tf_apply_exit_code != 0:
            raise Exception("Terraform apply failed")


if __name__ == "__main__":
    anyio.run(main)
