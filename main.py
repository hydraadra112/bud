import os

import click


@click.command()
def init():
    if os.path.exists("bud.json"):
        click.echo("Error: bud.json already exists in the current directory.")
        return

    with open("bud.json", "w") as f:
        f.write("{}")


def main():
    print("Hello from bud!")


if __name__ == "__main__":
    main()
