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


@bud.command()
@click.argument("amount", type=float)
def deposit(amount):
    if not os.path.exists("bud.json"):
        click.echo("Error: bud.json not found. Run 'bud init' first.")
        return

    if amount <= 0:
        click.echo("Error: Amount must be greater than zero.")
        return

    with open("bud.json", "r+") as f:
        data = json.load(f)

        data["balances"]["global"] += amount
        data["meta"]["last_updated"] = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        data["history"].append(
            {
                "timestamp": data["meta"]["last_updated"],
                "type": "add",
                "amount": amount,
                "category": None,
                "message": "Deposit to global funds",
            }
        )

        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()


@bud.command()
@click.argument("amount", type=float)
@click.argument("message", required=False, default="Withdraw money from global funds")
def withdraw(amount, message):
    if not os.path.exists("bud.json"):
        click.echo("Error: bud.json not found. Run 'bud init' first.")
        return

    if amount <= 0:
        click.echo("Error: Amount must be greater than zero.")
        return

    with open("bud.json", "r+") as f:
        data = json.load(f)

        if data["balances"]["global"] < amount:
            click.echo("Error: Insufficient global funds.")
            return

        data["balances"]["global"] -= amount
        data["meta"]["last_updated"] = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        data["history"].append(
            {
                "timestamp": data["meta"]["last_updated"],
                "type": "withdraw",
                "amount": amount,
                "category": None,
                "message": message,
            }
        )

        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()


@bud.command()
@click.argument("amount", type=float)
@click.argument("category")
def allocate(amount, category):
    if not os.path.exists("bud.json"):
        click.echo("Error: bud.json not found. Run 'bud init' first.")
        return

    if amount <= 0:
        click.echo("Error: Amount must be greater than zero.")
        return

    category = category.lower()

    with open("bud.json", "r+") as f:
        data = json.load(f)

        if category not in data["balances"]["categories"]:
            click.echo(f"Error: Category '{category}' does not exist.")
            return

        if data["balances"]["global"] < amount:
            click.echo("Error: Insufficient global funds.")
            return

        data["balances"]["global"] -= amount
        data["balances"]["categories"][category] += amount
        data["meta"]["last_updated"] = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        data["history"].append(
            {
                "timestamp": data["meta"]["last_updated"],
                "type": "budget",
                "amount": amount,
                "category": category,
                "message": f"Allocated to {category}",
            }
        )

        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()


@bud.command()
@click.argument("amount", type=float)
@click.argument("category")
@click.argument("message", required=False)
def spend(amount, category, message):
    if not os.path.exists("bud.json"):
        click.echo("Error: bud.json not found. Run 'bud init' first.")
        return

    if amount <= 0:
        click.echo("Error: Amount must be greater than zero.")
        return

    category = category.lower()
    with open("bud.json", "r+") as f:
        data = json.load(f)

        if category not in data["balances"]["categories"]:
            click.echo(f"Error: Category '{category}' does not exist.")
            return

        cat_balance = data["balances"]["categories"][category]
        global_balance = data["balances"]["global"]

        if cat_balance + global_balance < amount:
            click.echo("Error: Insufficient combined funds.")
            return

        if cat_balance >= amount:
            data["balances"]["categories"][category] -= amount
            if not message:
                message = f"Spent {amount} at {category} category"
        else:
            remainder = amount - cat_balance
            data["balances"]["categories"][category] = 0.0
            data["balances"]["global"] -= remainder
            click.echo(
                f"Notice: Category '{category}' short by ${remainder:.2f}. Covered from global funds."
            )
            if not message:
                message = f"Spent {amount} at {category} category (Covered {remainder:.2f} from global)"

        data["meta"]["last_updated"] = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        data["history"].append(
            {
                "timestamp": data["meta"]["last_updated"],
                "type": "use",
                "amount": amount,
                "category": category,
                "message": message,
            }
        )

        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()


@bud.group()
def category():
    pass


@category.command(name="new")
@click.argument("name")
def new_category(name):
    if not os.path.exists("bud.json"):
        click.echo("Error: bud.json not found. Run 'bud init' first.")
        return

    name = name.lower()

    with open("bud.json", "r+") as f:
        data = json.load(f)

        if name in data["balances"]["categories"]:
            click.echo(f"Error: Category '{name}' already exists.")
            return

        data["balances"]["categories"][name] = 0.0

        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()


def main():
    print("Hello from bud!")


if __name__ == "__main__":
    main()
