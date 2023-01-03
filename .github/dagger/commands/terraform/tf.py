import argparse
import os
import sys

import anyio
import dagger
from dagger.api.gen import Container


def __config() -> dict:
    """Configure the terraform commands.
    :return: A map of each terraform command with it's arguments.
    :rtype: dict[str, dict[str, list[str]]]
    """
    tf_state_bucket = os.getenv("TF_STATE_BUCKET", "sandbox-tf-terraform-states")
    tf_dynamo_table = os.getenv("TF_DYNAMO_TABLE", "sandbox-tf-remote")
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    deploy = os.getenv("DEPLOY", "sandbox-use1")
    tf_state_key = os.getenv("TF_STATE_KEY", "")

    cmd_config = {
        "init": {
            "exec": [
                f"-backend-config=bucket={tf_state_bucket}",
                f"-backend-config=key={tf_state_key}/terraform.tfstate",
                f"-backend-config=dynamodb_table={tf_dynamo_table}",
                f"-backend-config=region={aws_region}",
            ]
        },
        "plan": {
            "exec": [
                "plan",
                "-input=false",
                "-var-file=deploy/globals/inputs.tfvars",
                f"-var-file=deploy/{deploy}/inputs.tfvars",
            ]
        },
        "apply": {
            "exec": [
                "apply",
                "-input=false",
                "-var-file=deploy/globals/inputs.tfvars",
                f"-var-file=deploy/{deploy}/inputs.tfvars",
            ]
        },
        "destroy": {
            "exec": [
                "destroy",
                "-input=false",
                "-var-file=deploy/globals/inputs.tfvars",
                f"-var-file=deploy/{deploy}/inputs.tfvars",
            ]
        },
    }

    return cmd_config

def __validate_init() -> bool:
    """to be used if there is no .terraform dir"""
    pass

async def terraform_image(
    client: dagger.Client, mounted_dir: dagger.Directory
) -> Container:
    """Builds and returns the base terraform image as a dagger container object.
    :param client: The dagger client that will be used.
    :param mounted_dir: The directory where the Terraform config files are located.
    :return: A dagger container object.
    :rtype: dagger.Client.Container
    """
    tf_version = os.getenv("TF_VERSION", "1.3.1")
    return (
        client.container()
        .from_(f"hashicorp/terraform:{tf_version}")
        .with_mounted_directory("/src", mounted_dir)
        .with_workdir("/src")
    )


async def init(base: dagger.Container, exec: list) -> int:
    """Runs a terraform init.
    :param base: The base terraform image.
    :return: The exit code from the terraform init.
    :rtype: int
    """
    terraform_init = base.exec(exec)

    init_exit_code = await terraform_init.exit_code()

    if init_exit_code == 0:
        return 0
    else:
        return 1


async def plan(base: dagger.Container, exec: list) -> int:
    """Runs a terraform plan.
    :param base: The base terraform image.
    :return: The exit code from the terraform plan.
    :rtype: int
    """
    terraform_plan = base.exec(exec)

    plan_exit_code = await terraform_plan.exit_code()

    if plan_exit_code == 0:
        return 0
    else:
        return 1


async def apply(base: dagger.Container, exec: list) -> int:
    """Runs a terraform apply.
    :param base: The base terraform image.
    :return: The exit code from the terraform apply.
    :rtype: int
    """
    terraform_apply = base.exec(exec)

    apply_exit_code = await terraform_apply.exit_code()

    if apply_exit_code == 0:
        return 0
    else:
        return 1


async def destroy(base: dagger.Container) -> int:
    """Runs a terraform destroy.
    :param base: The base terraform image.
    :return: The exit code from the terraform destroy.
    :rtype: int
    """
    terraform_destroy = base.exec(exec)

    destroy_exit_code = await terraform_destroy.exit_code()

    if destroy_exit_code == 0:
        return 0
    else:
        return 1


async def main(args: argparse.Namespace) -> int:
    config = __config()
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:
        # mount terraform code into `terraform` image
        terraform_dir = client.host().directory(args.work_dir)

        # initalize the `terraform` container object to use
        terraform_base_image = await terraform_image(client, mounted_dir=terraform_dir)

        if args.init:
            # run a terraform init
            tf_init_exit_code = await init(
                base=terraform_base_image, exec=config["init"]["exec"]
            )
            if tf_init_exit_code != 0:
                raise Exception("Terraform init failed!")
        elif args.plan:
            __validate_init()
            # run a terraform plan
            tf_plan_exit_code = await plan(
                base=terraform_base_image, exec=config["plan"]["exec"]
            )
            if tf_plan_exit_code != 0:
                raise Exception("Terraform plan failed!")
        elif args.apply:
            # run a terraform apply
            tf_apply_exit_code = await apply(
                base=terraform_base_image, exec=config["apply"]["exec"]
            )
            if tf_apply_exit_code != 0:
                raise Exception("Terraform apply failed")
        else:
            raise NotImplementedError(f"The command {args.command} is not implemented!")


if __name__ == "__main__":
    anyio.run(main)
