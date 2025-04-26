# OS Scheduling Algorithms – Assignment 01

A Python project that lets you play with classic CPU–scheduling algorithms (FCFS, SJF, Priority, Round Robin, etc.) .

## 1. Clone the repo

```bash
git clone https://github.com/malakkbl/Assignment01OS.git
cd Assignment01OS
```

## 2. Install the only external package we use

```bash
pip install flask          
```
---

## 4. Run from the terminal

```bash
python main.py
```

You’ll be prompted to

1. choose the algorithm,
2. enter process data (arrival & burst, plus priority if required),
3. give a quantum if you picked Round Robin,
4. see a schedule + metrics printed back.

---

## 5. Run the web interface

```bash
python interface/interface.py
```

Then open <http://127.0.0.1:5000/> in your browser and fill in the form.

---

## Folder map (just so you know)

```
algorithms/         individual algorithm implementations
interface/          Flask app  (interface.py + Jinja templates)
main.py             CLI entry point
process.py          Process data-class
utils.py            helper functions
```