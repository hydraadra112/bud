#!/usr/bin/env python3
import json
import math
import os
from datetime import datetime, timezone

import click

RESERVED_CATEGORY_NAMES = {"global"}


def normalize_name(name):
    """Strip whitespace and lowercase a category name."""
    return name.strip().lower()


def validate_amount(amount):
    """
    Returns an error message (str) if the amount is invalid, else None.
    Rejects NaN, +/-Infinity, and non-positive values.
    """
    if not math.isfinite(amount):
        return (
            "Error: Amount must be a finite number (NaN and Infinity are not allowed)."
        )
    if amount <= 0:
        return "Error: Amount must be greater than zero."
    return None


def is_reserved(name):
    return name in RESERVED_CATEGORY_NAMES


@click.group(help="A lightweight, keyboard-driven personal budget tracker")
def bud():
    pass


@bud.command(help="Creates a bud.json file in the current working directory.")
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite an existing bud.json, discarding all current data.",
)
def init(force):
    exists = os.path.exists("bud.json")

    if exists and not force:
        click.echo("Error: bud.json already exists in the current directory.")
        click.echo(
            "Tip: Use 'bud init --force' to overwrite it (this erases all existing data)."
        )
        return

    if exists and force:
        click.echo("Warning: Overwriting existing bud.json. All prior data is lost.")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    template = {
        "meta": {"version": "1.0", "last_updated": now},
        "balances": {"global": 0.0, "categories": {}, "archived_categories": []},
        "history": [],
    }

    with open("bud.json", "w") as f:
        json.dump(template, f, indent=2)

    click.echo("Initiated bud ledger (bud.json) in current directory.")
    click.echo("Tip: Run 'bud flow' or 'bud --help' for the basic commands.")


@bud.command(help="Displays the remaining balance and the history of a given category.")
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

    category = normalize_name(category)

    with open("bud.json", "r") as f:
        data = json.load(f)

    if category not in data["balances"]["categories"]:
        click.echo(f"Error: Category '{category}' does not exist.")
        return

    balance = data["balances"]["categories"][category]
    click.echo(f"Category: {category}")
    click.echo(f"Remaining Balance: {balance:.2f}")
    click.echo("\nHistory:")

    filtered_history = [h for h in data["history"] if h.get("category") == category]

    if not filtered_history:
        click.echo("  No history found for this category.")
        return

    for h in filtered_history[-entries:]:
        click.echo(
            f"  [{h['timestamp']}] {h['type'].upper()} - {h['amount']:.2f} | {h['message']}"
        )


@bud.command(help="Adds funds in the global money pool.")
@click.argument("amount", type=float)
def deposit(amount):
    if not os.path.exists("bud.json"):
        click.echo("Error: bud.json not found. Run 'bud init' first.")
        return

    error = validate_amount(amount)
    if error:
        click.echo(error)
        click.echo("Tip: Enter a positive, finite number, e.g. 'bud deposit 50'.")
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
            f"Deposited {amount:.2f} to global funds. New global funds are {new_total:.2f}"
        )


@bud.command(help="Withdraws funds from the global money pool")
@click.argument("amount", type=float)
@click.argument("message", required=False, default="Withdraw money from global funds")
def withdraw(amount, message):
    if not os.path.exists("bud.json"):
        click.echo("Error: bud.json not found. Run 'bud init' first.")
        return

    error = validate_amount(amount)
    if error:
        click.echo(error)
        click.echo("Tip: Enter a positive, finite number, e.g. 'bud withdraw 20'.")
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
            f"Withdrawn {amount:.2f} from global funds. New global funds are {new_total:.2f}."
        )


@bud.command(help="Allocates funds to a given category.")
@click.argument("amount", type=float)
@click.argument("category")
def allocate(amount, category):
    if not os.path.exists("bud.json"):
        click.echo("Error: bud.json not found. Run 'bud init' first.")
        return

    error = validate_amount(amount)
    if error:
        click.echo(error)
        click.echo(
            "Tip: Enter a positive, finite number, e.g. 'bud allocate 25 groceries'."
        )
        return

    category = normalize_name(category)

    if not category:
        click.echo("Error: Category name cannot be empty.")
        return

    if is_reserved(category):
        click.echo(
            f"Error: '{category}' is a reserved name and can't be used as a category."
        )
        return

    with open("bud.json", "r+") as f:
        data = json.load(f)

        if category not in data["balances"]["categories"]:
            click.echo(
                f"Notice: Category '{category}' does not currently exist.\nCreating '{category}' now."
            )
            data["balances"]["categories"][category] = 0.0

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
            f"Allocated {amount:.2f} to {category}.\n"
            f"Total funds for {category}: {new_total_category:.2f}.\n"
            f"Global funds left: {new_total_global:.2f}"
        )


@bud.command(help="Spends funds on any given category.")
@click.argument("amount", type=float)
@click.argument("category")
@click.argument("message", required=False)
def spend(amount, category, message):
    if not os.path.exists("bud.json"):
        click.echo("Error: bud.json not found. Run 'bud init' first.")
        return

    error = validate_amount(amount)
    if error:
        click.echo(error)
        click.echo(
            "Tip: Enter a positive, finite number, e.g. 'bud spend 12 groceries \"eggs and milk\"'."
        )
        return

    category = normalize_name(category)
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
            json_msg = message or f"Spent {amount:.2f} from {category}."
            echo_msg = (
                f"Spent {amount:.2f} at {category}.\n"
                f"Total funds left for {category}: {data['balances']['categories'][category]:.2f}."
            )
        else:
            remainder = amount - cat_balance
            data["balances"]["categories"][category] = 0.0
            data["balances"]["global"] -= remainder
            json_msg = (
                message or f"Spent {amount:.2f} from {category} (split with global)."
            )
            echo_msg = (
                f"Notice: {category} short by {remainder:.2f}. Covered from global funds.\n"
                f"Total global funds left: {data['balances']['global']:.2f}"
            )

        data["meta"]["last_updated"] = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        data["history"].append(
            {
                "timestamp": data["meta"]["last_updated"],
                "type": "spend",
                "amount": amount,
                "category": category,
                "message": json_msg,
            }
        )

        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()
        click.echo(echo_msg)
        click.echo(f"Tip: Run 'bud report {category}' to view the updated history.")


@bud.command(help="Shows the typical command pipeline, from init to archive.")
def flow():
    click.echo("Typical bud workflow, start to finish:\n")
    click.echo("  bud init                          # Init ledger")
    click.echo("  bud category new food             # Create category")
    click.echo("  bud deposit 2500.00               # Add global funds")
    click.echo("  bud allocate 400.00 food          # Move funds to category")
    click.echo('  bud spend 15.50 food "Burrito"    # Log expense')
    click.echo("  bud report food                   # View category status")
    click.echo("  bud category archive food         # Close cat, return funds")
    click.echo("\nFunds live in one of two places: the global pool, or a category.")
    click.echo(
        "Deposit fills the global pool. Allocate moves money from global into a category. "
        "Spend draws from a category first, then global if it runs short. Archiving a "
        "category returns whatever's left to the global pool."
    )
    click.echo(
        "\nRun any command with --help for its full options, e.g. 'bud spend --help'."
    )


@bud.group(help="For category related commands (create, archive, list)")
def category():
    pass


@category.command(name="new", help="Creates a new category for you to allocate funds.")
@click.argument("name")
def new_category(name):
    if not os.path.exists("bud.json"):
        click.echo("Error: bud.json not found. Run 'bud init' first.")
        return

    name = normalize_name(name)

    if not name:
        click.echo("Error: Category name cannot be empty.")
        return

    if is_reserved(name):
        click.echo(
            f"Error: '{name}' is a reserved name and can't be used as a category."
        )
        return

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


@category.command(
    name="list", help="Lists down all created categories with their remaining budget."
)
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
        click.echo(f"- {name}: {balance:.2f}")


@category.command(
    name="archive",
    help="Archives an existing category. History is preserved, and allocated funds will return to the global fund pool.",
)
@click.argument("name")
def archive_category(name):
    if not os.path.exists("bud.json"):
        click.echo("Error: bud.json not found. Run 'bud init' first.")
        return

    name = normalize_name(name)

    if is_reserved(name):
        click.echo(
            f"Error: '{name}' is a reserved name and can't be archived as a category."
        )
        return

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
                "message": f"Archived category '{name}', returned {balance:.2f} to global",
            }
        )

        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

    click.echo(f"Category '{name}' archived. Returned {balance:.2f} to global funds.")


bud.add_command(category)

if __name__ == "__main__":
    bud()
