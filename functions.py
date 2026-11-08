"""
functions.py  -  MEMBER 2: reusable functions and input validation.

Every function here either (a) asks the user for ONE kind of value and keeps
asking until the value is valid, or (b) prints data in a readable table.
"""

from datetime import datetime


# ----------------------------------------------------------------------
# INPUT FUNCTIONS (they loop until the user gives valid input)
# ----------------------------------------------------------------------
def get_text(prompt, required=True):
    """Ask for text. If required, keep asking until it is not empty."""
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print("  This field is required. Please try again.")


def get_text_default(prompt, current):
    """Ask for new text; pressing Enter keeps the current value (for updates)."""
    value = input(f"{prompt} [{current}]: ").strip()
    return value if value else current


def get_phone(prompt, current=None):
    """Ask for a contact number (digits and dashes only, at least 7 digits)."""
    while True:
        text = f"{prompt} [{current}]: " if current else prompt
        value = input(text).strip()
        if current and not value:
            return current
        digits = value.replace("-", "").replace(" ", "")
        if digits.isdigit() and len(digits) >= 7:
            return value
        print("  Enter a valid number (digits and dashes, at least 7 digits).")


def get_int(prompt):
    """Ask for a whole number (type conversion with error handling)."""
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("  Please enter a whole number.")


def get_amount(prompt, allow_zero=False):
    """Ask for a money amount. Must be a number, positive (or zero if allowed)."""
    while True:
        try:
            amount = float(input(prompt).strip())
        except ValueError:
            print("  Please enter a number, for example 1500 or 1500.50.")
            continue                                   # ask again
        if amount > 0 or (allow_zero and amount == 0):
            return amount
        print("  The amount must be greater than 0." if not allow_zero
              else "  The amount cannot be negative.")


def get_choice(prompt, options):
    """Show a numbered list of options and return the one the user picks."""
    print(prompt)
    for number, option in enumerate(options, start=1):
        print(f"  {number}. {option}")
    while True:
        pick = get_int("Choose a number: ")
        if 1 <= pick <= len(options):
            return options[pick - 1]
        print(f"  Please choose between 1 and {len(options)}.")


def get_date(prompt, allow_blank=False):
    """Ask for a date as YYYY-MM-DD. Returns text, or None if blank is allowed."""
    while True:
        value = input(prompt).strip()
        if not value and allow_blank:
            return None
        try:
            datetime.strptime(value, "%Y-%m-%d")       # checks the format is real
            return value
        except ValueError:
            print("  Use the format YYYY-MM-DD, for example 2026-11-08.")


def confirm(prompt):
    """Ask a yes/no question. Returns True only for 'y' or 'yes'."""
    answer = input(f"{prompt} (y/n): ").strip().lower()
    return answer in ("y", "yes")


def pause():
    """Wait for Enter so the user can read the screen."""
    input("\nPress Enter to continue...")


# ----------------------------------------------------------------------
# OUTPUT FUNCTIONS
# ----------------------------------------------------------------------
def money(value):
    """Format a number as pesos, e.g. 1500 -> 'P1,500.00'."""
    return f"P{value:,.2f}"


def print_table(rows, columns):
    """Print rows in aligned columns.

    columns is a list of (heading, key, width) tuples, for example
    [("ID", "customer_id", 4), ("Name", "full_name", 20)].
    """
    if not rows:
        print("\n  No records found.")
        return
    line = " | ".join(f"{heading:<{width}}" for heading, _, width in columns)
    print("\n" + line)
    print("-" * len(line))
    for row in rows:
        cells = []
        for _, key, width in columns:
            value = row[key]
            if isinstance(value, float):
                value = f"{value:,.2f}"
            cells.append(f"{str(value if value is not None else '-')[:width]:<{width}}")
        print(" | ".join(cells))
    print(f"\n  {len(rows)} record(s).")


CUSTOMER_COLUMNS = [("ID", "customer_id", 4), ("Name", "full_name", 22),
                    ("Contact", "contact_number", 15), ("Address", "address", 20)]

DEVICE_COLUMNS = [("ID", "device_id", 4), ("Type", "device_type", 8),
                  ("Brand", "brand", 10), ("Model", "model", 12),
                  ("Serial", "serial_number", 10), ("Owner", "full_name", 20)]

REPAIR_COLUMNS = [("ID", "repair_id", 4), ("Customer", "full_name", 18),
                  ("Type", "device_type", 7), ("Problem", "problem_description", 24),
                  ("Received", "date_received", 10), ("Status", "status", 11),
                  ("Charge", "service_charge", 9), ("Paid", "total_paid", 9),
                  ("Balance", "balance", 9)]

PAYMENT_COLUMNS = [("ID", "payment_id", 4), ("Repair", "repair_id", 6),
                   ("Amount", "amount", 10), ("Date", "payment_date", 10)]
