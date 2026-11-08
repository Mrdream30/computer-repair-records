# Test Cases

Fill the **Actual result** and **Status** columns when YOU run each test on your own
computer, and attach screenshots. Rows marked (auto) are also checked by
`python tests/test_database.py`.

| # | Test | Steps | Expected result | Actual result | Status |
|---|---|---|---|---|---|
| 1 | Valid input (auto) | Customers > Add, enter a name and number 0912-345-6789 | Record accepted and saved | | |
| 2 | Invalid input | Add customer, type `abc` as contact number | Message shown, asks again, no crash | | |
| 3 | Invalid menu choice | At main menu type `9` | "Invalid choice" message | | |
| 4 | Missing records (auto) | Customers > Search for `zzz` | "No records found." | | |
| 5 | Duplicate identifier (auto) | Add a customer with an existing contact number | "Duplicate value" message | | |
| 6 | Search (auto) | Search customer `Sample`; search repairs by status | Matching records listed | | |
| 7 | Update (auto) | Update customer 1; try update ID 999 | Updated; ID 999 gives "not found" | | |
| 8 | Delete | Delete a customer with no devices, answer `n` then `y` | `n` cancels; `y` deletes | | |
| 9 | Delete linked record (auto) | Delete customer 1 (has devices) | Blocked with a clear message | | |
| 10 | Partial payment (auto) | Pay part of a repair, view payments | Balance = charge − payments | | |
| 11 | Overpayment (auto) | Pay more than the balance | Refused with a message | | |
| 12 | Persistence | Add a record, exit, run again, view records | Record is still there | | |
| 13 | Analysis (auto) | Analytics > Revenue summary | Numbers match the data | | |
| 14 | Charts | Analytics > Generate charts | 3 PNG files appear in `charts/` | | |
| 15 | Fresh setup | Clone repo into a new folder, follow README | Program starts and works | | |
