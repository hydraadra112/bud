<div align="center">
<img width="300" height="300" alt="bud_logo_v3" src="https://github.com/user-attachments/assets/105b33b8-ebcc-451a-bc35-7c729ec46365" />
<h1>bud</h1>

<p>A lightweight, keyboard-driven personal budget tracker for terminal users </p>
</div>

---

<table align="center" style="border-collapse: collapse; border: none;">
  <tr style="border: none;">
    <td style="border: none; padding: 5px;"><img height="380" alt="CLI Commands" src="https://github.com/user-attachments/assets/ee08e230-ccfa-4975-bf00-2713c2325398" /></td>
    <td style="border: none; padding: 5px;"><img height="380" alt="ASCII Dashboard" src="https://github.com/user-attachments/assets/fa658b10-5552-4ef3-ae7b-390daf5d2630" /></td>
  </tr>
</table>

> [!NOTE]
> Currently only supports Linux distros. Will add Windows support soon.

## How to install?
Simply execute the following commands:
```bash
# 1. Clone the repository wherever you want
git clone https://github.com/hydraadra112/bud.git
cd bud

# 2. Make it executable
chmod +x bud.py

# 3. Symlink using the absolute current path
ln -s "$(pwd)/bud.py" ~/.local/bin/bud

# 4. Initialize the database in ~/.local/share/bud/
bud init
```

## How to use?
```bash
bud init                          # Init ledger
bud category new food             # Create category
bud deposit 2500.00               # Add global funds
bud allocate 400.00 food          # Move funds to category
bud spend 15.50 food "Burrito"    # Log expense
bud report food                   # View category status
bud category archive food         # Close cat, return funds
```

- Deposit fills the global pool.
- Allocate moves money from global into a category.
- Spend draws from a category first, then global if it runs short.
- Archiving a category returns whatever's left to the global pool.

## Why did I make this?
I designed this little CLI tool for personal use, for managing my own budget, especially that I am transitioning into my professional life. I prefer making things work in my own workspace rather than leaving, and looking at a spreadsheet. I know there are people out there like me, so I decided to share this.
