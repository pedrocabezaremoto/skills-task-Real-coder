# Validation Checklist Common Errors

> Fuente: `guia8/gi7.md` | Proyecto: Real Coder (Outlier)

---

🛠 Validation Checklist: Common Errors 1. The (app) Folder Structure Ensure your root directory contains exactly these files/folders. No more, no less: ● codebase.zip ● tests.zip ● Dockerfile ● parsing.py ● run.sh

2. The Golden Rule of ZIP Files The way you compress these files is critical. Follow these specific methods:
File Internal Structure (When opened) How to Zip It
tests.zip Should contain the tests folder first. Zip the folder itself.
codebase.zip Should contain the contents only (no parent folder).
Zip the files inside the folder.

⚠ Warning: Do not make codebase.zip nested (e.g., codebase.zip → codebase/ → files). It must be codebase.zip → files.

3. File Integrity & Cursor Management While using Cursor, you must be extremely careful with its "Auto-edit" or Agent features.
run.sh and parsing.py ● Action: Monitor these files closely.

● Constraint: Do not allow any changes to the sections labeled "DO NOT MODIFY."
verification.sh ● Action: You are permitted to edit one section only: your Path.
 ● Constraint: Do not update anything else. Ensure your Cursor agent does not
"hallucinate"

improvements

or

changes

to

other

lines

in

this

file.