import json
import os
from datetime import datetime, timezone

import click


@click.group()
def bud():
    pass


@click.command()
def init():
    if os.path.exists("bud.json"):
        click.echo("Error: bud.json already exists in the current directory.")
        return

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    template = {
        "meta": {"version": "1.0", "last_updated": now},
        "balances": {"global": 0.0, "categories": {}, "archived_categories": []},
        "history": [],
    }

    with open("bud.json", "w") as f:
        json.dump(template, f, indent=2)


def main():
    print("Hello from bud!")


if __name__ == "__main__":
    main()
