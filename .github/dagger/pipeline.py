import argparse
import sys
import os

from commands.terraform.tf import main as tf

def __validate_tf_project(project: str) -> bool:
    """validate the terraform project exists."""
    for dir in os.listdir("./"):
        if os.path.isdir(dir) and dir == project:
            return True
    return False


def __create_tf_parser(subparser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Create the terraform parser and return it.
    :parser subparser: The subparser to add the terraform parser to.
    :return: The terraform parser.
    :rtype: argparse.ArgumentParser
    """
    parser = subparser.add_parser("terraform")
    parser.add_argument(
        "-i",
        "--init",
        action="store_true",
        help="Run terraform init.",
    )
    parser.add_argument("-p", "--plan", action="store_true", help="Run terraform plan.")
    parser.add_argument(
        "-a", "--apply", action="store_true", help="Run terraform apply."
    )
    parser.add_argument(
        "-d", "--destroy", action="store_true", help="Run terraform destroy."
    )
    parser.add_argument(
        "-w",
        "--work-dir",
        nargs="?",
        type=__validate_tf_project,
        required=True,
        help="The work directory where the Terraform project is located relative to the repository.",
    )
    return parser


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="bob",
        description="A command line tool to run our pipelines.",
    )

    subparser = parser.add_subparsers(dest="command")

    # add the terraform paraser with all it's arguments added.
    tf_parser = __create_tf_parser(subparser)

    help = subparser.add_parser("help", help="Show the help for a specific command.")
    help.add_argument("help_cmd", nargs="?", help="Command to show help for.")

    if len(argv) == 0:
        parser.print_help()

    args = parser.parse_args(argv)

    if args.command == "help" and args.help_cmd:
        parser.parse_args([args.help_cmd, "--help"])
        return 0
    elif args.command == "help":
        parser.parse_args(["--help"])
        return 0

    if args.command == "terraform":
        tf(args)
    else:
        raise NotImplementedError(f"The command {args.command} is not implemented!")

if __name__ == "__main__":
    raise SystemExit(main())
