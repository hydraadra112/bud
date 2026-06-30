#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone

import click


@click.group()
def bud():
    pass


@bud.command()
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

    click.echo("Initiated bud ledger (bud.json) in current directory.")


@bud.command()
@click.argument("category")
@click.option(
    "-n",
    "--entries",
    type=int,
    default=5,
    help="Number of history entries to show.",
)
def report(category, entries):
    if not os.path.exists("bud.json"):
        click.echo("Error: bud.json not found. Run 'bud init' first.")
        return

    category = category.lower()

    with open("bud.json", "r") as f:
        data = json.load(f)

    if category not in data["balances"]["categories"]:
        click.echo(f"Error: Category '{category}' does not exist.")
        return

    balance = data["balances"]["categories"][category]
    click.echo(f"Category: {category}")
    click.echo(f"Remaining Balance: ${balance:.2f}")
    click.echo("\nHistory:")

    filtered_history = [h for h in data["history"] if h.get("category") == category]

    if not filtered_history:
        click.echo("  No history found for this category.")
        return

    for h in filtered_history[-entries:]:
        click.echo(
            f"  [{h['timestamp']}] {h['type'].upper()} - ${h['amount']:.2f} | {h['message']}"
        )


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

        new_total = amount + data["balances"]["global"]

        data["balances"]["global"] = new_total
        data["meta"]["last_updated"] = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        data["history"].append(
            {
                "timestamp": data["meta"]["last_updated"],
                "type": "deposit",
                "amount": amount,
                "category": None,
                "message": "Deposit to global funds",
            }
        )

        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

        click.echo(
            f"Deposited {amount} to global funds. New global funds are {new_total}"
        )


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

        new_total = data["balances"]["global"] - amount
        data["balances"]["global"] = new_total
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

        click.echo(
            f"Withdrawn {amount} from global funds. New global funds are {new_total}."
        )


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

        new_total_global = data["balances"]["global"] - amount
        data["balances"]["global"] = new_total_global

        new_total_category = amount + data["balances"]["categories"][category]

        data["balances"]["categories"][category] = new_total_category
        data["meta"]["last_updated"] = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        data["history"].append(
            {
                "timestamp": data["meta"]["last_updated"],
                "type": "allocate",
                "amount": amount,
                "category": category,
                "message": f"Allocated to {category}",
            }
        )

        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

        click.echo(
            f"Allocated {amount} to {category}.\nTotal funds for {category}: {new_total_category}.\nGlobal funds left: {new_total_global}"
        )


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
            click.echo(f"Error: Insufficient funds from {category} and global funds.")
            return

        if cat_balance >= amount:
            data["balances"]["categories"][category] -= amount
            if not message:
                message = f"Spent {amount} at {category}.\nTotal funds left for {category}: {cat_balance - amount}."
        else:
            remainder = amount - cat_balance
            data["balances"]["categories"][category] = 0.0
            data["balances"]["global"] -= remainder
            if not message:
                global_funds_left = data["balances"]["global"]
                message = f"Notice: {category} short by ${remainder:.2f}. Covered from global funds.\nTotal global funds left: {global_funds_left}"

        data["meta"]["last_updated"] = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        data["history"].append(
            {
                "timestamp": data["meta"]["last_updated"],
                "type": "spend",
                "amount": amount,
                "category": category,
                "message": message,
            }
        )

        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()
        click.echo(message)


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

    click.echo(f"Added '{name}' to categories.")


@category.command(name="list")
def list_categories():
    if not os.path.exists("bud.json"):
        click.echo("Error: bud.json not found. Run 'bud init' first.")
        return

    with open("bud.json", "r") as f:
        data = json.load(f)

    categories = data["balances"]["categories"]
    if not categories:
        click.echo("No categories found.")
        return

    for name, balance in categories.items():
        click.echo(f"- {name}: ${balance:.2f}")


@category.command(name="archive")
@click.argument("name")
def archive_category(name):
    if not os.path.exists("bud.json"):
        click.echo("Error: bud.json not found. Run 'bud init' first.")
        return

    name = name.lower()

    with open("bud.json", "r+") as f:
        data = json.load(f)

        if name not in data["balances"]["categories"]:
            click.echo(f"Error: Category '{name}' does not exist.")
            return

        balance = data["balances"]["categories"].pop(name)
        data["balances"]["global"] += balance

        if name not in data["balances"]["archived_categories"]:
            data["balances"]["archived_categories"].append(name)

        data["meta"]["last_updated"] = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        data["history"].append(
            {
                "timestamp": data["meta"]["last_updated"],
                "type": "archive",
                "amount": balance,
                "category": name,
                "message": f"Archived category '{name}', returned ${balance:.2f} to global",
            }
        )

        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

    click.echo(f"Category '{name}' archived. Returned ${balance:.2f} to global funds.")


bud.add_command(category)

if __name__ == "__main__":
    bud()
