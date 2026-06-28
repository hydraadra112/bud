<div align="center">
<img width="300" height="300" alt="bud_logo_v3" src="https://github.com/user-attachments/assets/105b33b8-ebcc-451a-bc35-7c729ec46365" />
<h1>bud</h1>

<p>A lightweight, keyboard-driven personal budget tracker for power users </p>
</div>

---

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

Another alternative:
- Add a shebang at the very top of the file: `#!/usr/bin/env python3`
- Make it executable via `chmod +x bud.py`
Can now run:
```bash
./bud.py init
./bud.py deposit 2400
./bud.py allocate 400 food
```
