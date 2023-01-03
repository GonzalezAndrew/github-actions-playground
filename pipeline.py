import anyio
import dagger


async def pipeline(client: dagger.Client):
    # Fetch source code from github
    source_code = await (
        client.git("https://github.com/kpenfound/greetings-api.git")
        .branch("main")
        .tree().id()
    )

    # Generic golang builder image
    builder = (
        client.container()
        .from_("golang:1.19-alpine")
        .with_workdir("/usr/src/app")
    )

    # Compile the go binary from the source code
    app_binary = await (
        builder.with_mounted_directory("/usr/src/app", source_code.value)
        .exec(["sh", "-c", "go build -v -o /usr/local/bin/app"])
        .file("/usr/local/bin/app").id()
    )

    # Create an FS layer with only the binary
    image_fs = await (
        client.container()
        .from_("alpine:3.16").fs()
        .with_file("/usr/local/bin/app", app_binary.value).id()
    )

    # Publish a new container based on alpine, containing the app binary
    image = await (
        client.container()
        .with_fs(image_fs.value)
        .with_entrypoint("/usr/local/bin/app")
        .publish("samalba/greetings-api")
    )

    print("Run it locally:")
    print(f"docker run -it --rm -p 5000:5000 {image.value}")


async def main():
    async with dagger.Connection() as client:
        await pipeline(client)

if __name__ == "__main__":
    anyio.run(main)