# Computer Repair Service Records Management System

DSA 214 – Programming for Data Science, Final Laboratory Activity
Scenario: **Computer Repair Service Records** · Interface: command line (CLI)

A Python + SQLite program for a computer repair shop. It stores customers,
their devices (Desktop or Laptop), repair requests with service charges, and
partial payments with remaining balances. It also produces summaries and charts.

## Requirements
- Python 3.9 or newer
- matplotlib (for charts)

## Installation
```
git clone <your-repository-url>
cd <project-folder>
pip install -r requirements.txt
```

## Run
```
python main.py
```
On the first run the program creates `database/repair_records.db` and loads
**simulated** sample records (invented names; not real people). Records are saved
automatically and are still there the next time you run the program.

## Files
| File | Purpose | Member |
|---|---|---|
| `database.py` | Database connection, tables, SQL/CRUD, summary queries | 1 |
| `functions.py` | Input validation and display functions | 2 |
| `main.py` | Main menu and program flow | 2 |
| `analytics.py` | Three measures and three charts | 3 |
| `tests/` | Automatic checks and the test case table | 4 |

## Database design
`customers 1──* devices 1──* repairs 1──* payments`

## Features
Add, view, search, update and delete (with confirmation) for customers,
devices, repairs and payments; revenue summary, repair status breakdown,
average turnaround and top brands; charts saved in `charts/`.

## Tests
```
python tests/test_database.py
```

## Data note
All sample data is simulated for demonstration only.
