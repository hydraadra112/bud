# bud
A lightweight, keyboard-driven personal budget tracker and power users.

How to use? (Temporary, for testing)
```bash
# Setup local shortcut
alias bud="uv run python $(pwd)/bud.py"

bud init                          # Init ledger
bud category new food             # Create category
bud deposit 2500.00               # Add global funds
bud allocate 400.00 food          # Move funds to category
bud spend 15.50 food "Burrito"    # Log expense
bud report food                   # View category status
bud category archive food         # Close cat, return funds
```
