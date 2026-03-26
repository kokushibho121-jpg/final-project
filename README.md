# AI Memory Leak Detector

This project is a desktop dashboard for memory leak and resource anomaly detection.
Python is used for the UI and graph.
The main scoring idea is a small Isolation Forest style detector.
The C file still shows basic memory management with `malloc` and `free`.

## Project structure

```text
final_project/
|-- c_core/
|   |-- build.ps1
|   `-- monitor_core.c
|-- memory_leak_detector/
|   |-- __init__.py
|   |-- app.py
|   `-- monitor.py
|-- main.py
|-- requirements.txt
`-- README.md
```

## What it does

- shows 4 dashboard cards
- lets you set a memory threshold
- simulates memory and CPU values
- uses an Isolation Forest style score
- plots memory and CPU on a live graph
- exports warning logs to CSV
- shows `System Stable` or `System Warning`

## C concepts used

- `struct`
- functions
- `if` and `else`
- variables
- `malloc` and `free`
- random number logic
- basic anomaly checking

## Build the C file

```powershell
cd c_core
powershell -ExecutionPolicy Bypass -File .\build.ps1
cd ..
```

## Run the project

```powershell
pip install -r requirements.txt
python main.py
```

Write a threshold value in the box, then press `Start`.
If the C DLL does not load, the app still runs with the Python fallback.
