"""
Create a multi-build pipeline for a Go application.
"""

'''
async def build_image_from_tag(tag: str, client):
    
        base_image = ( 
            client.container()
            .from_(tag)  
            .exec(["mkdir", "-p", "/output"])
            .exec(["mkdir", "-p", "/.terraform.d/plugin-cache"])
        )

        print(f"Building Docker Image for tag {tag}")

        await base_image.exit_code()
        return base_image

async def run_module(module: str, image, prev_runner_output, apply: bool, client):

    terraform_action  = (
        image
        .with_directory("/input", prev_runner_output if prev_runner_output else client.directory())
        .with_mounted_directory("/src",local_src)

        .exec(["terraform, init"])
        .exec(["terraform", "plan", "-var-file", "/input/prev_output.json", "-input=false"])
        .exec(["/bin/bash", "-c", "terraform output -json | jq 'with_entries(.value |= .value)'"], redirect_stdout="/output/prev_output.json")

    )
    # THIS NOW WORKS WITHOUT EXIT CODE
    print(f"finished running terraform module {module}")
    # create empty directory to hold build outputs
    outputs = client.directory()
    return outputs.with_directory("/", terraform_action.directory("/output"))
    
async def run_workflow(apply):
    runner_image_tag = os.getenv('INFRA_RUNNER_IMAGE_TAG') #https://github.com/Wi3ard/docker-terraform-gcloud-aws/blob/master/Dockerfile
    config = dagger.Config(log_output=sys.stderr, execute_timeout=60)
    
    async with dagger.Connection(config) as client: 
        runner_image = infra_runner.build_image_from_tag(runner_image_tag, client)
        project_output = terraform.run_module("project/gcp", runner_image, None, apply, client) 
        terraform.run_module("serverless/gcp/cloudrun", runner_image, project_output, apply, client)
        network_output = terraform.run_module("network/gcp", runner_image, project_output, apply, client)
        terraform.run_module("loadbalancer/gcp/serverless", runner_image, network_output, apply, client)
        terraform.run_module("cluster/k8s/gcp",runner_image, network_output, apply, client)
        bastion_output = terraform.run_module("bastion/gcp", runner_image, network_output, apply, client)
        await bastion_output.entries()
'''
import itertools
import sys

import anyio
import graphql

import dagger


async def build():
    print("Building with Dagger")

    # define build matrix
    oses = ["linux", "darwin"]
    arches = ["amd64", "arm64"]

    # initialize dagger client
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:

        # get reference to the local project
        src = client.host().directory(".")

        # create empty directory to put build outputs
        outputs = client.directory()

        golang = (
            # get `golang` image
            client.container()
            .from_("golang:latest")
            # mount source code into `golang` image
            .with_mounted_directory("/src", src)
            .with_workdir("/src")
        )

        for goos, goarch in itertools.product(oses, arches):
            # create a directory for each OS and architecture
            path = f"build/{goos}/{goarch}/"

            build = (
                golang
                # set GOARCH and GOOS in the build environment
                .with_env_variable("GOOS", goos)
                .with_env_variable("GOARCH", goarch)
                .with_exec(["go", "build", "-o", path])
            )

            # add build to outputs
            outputs = outputs.with_directory(path, build.directory(path))

        # write build artifacts to host
        await outputs.export(".")


if __name__ == "__main__":
    try:
        anyio.run(build)
    except graphql.GraphQLError as e:
        print(e.message, file=sys.stderr)
        sys.exit(1)