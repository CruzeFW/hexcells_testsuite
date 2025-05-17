import subprocess
import time
import psutil
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
from datetime import datetime

# Pfade & Setup
LEVEL_DIR = Path(r"D:\Datein\Stuff\FHTechnikum\6Semester\hexAlgo\extra")
SOLVER_PATH = r"D:\Datein\Stuff\FHTechnikum\6Semester\hexAlgo\target\debug\hexcells-solver.exe"
SCRIPT_DIR = Path(__file__).parent.resolve()
timestamp = datetime.now().strftime("%d%m%y_%H%M")
RUN_DIR = SCRIPT_DIR / "solver_runs" / timestamp
RUN_DIR.mkdir(parents=True, exist_ok=True)
CSV_OUTPUT = RUN_DIR / "solver_times.csv"

# Level-Dateien laden
level_files = sorted(LEVEL_DIR.glob("*.txt"))
data = []

# Hauptlauf: alle Levels, je 10 Wiederholungen
for level_file in level_files:
    with open(level_file, "r") as f:
        level_str = f.read()

    level_name = level_file.stem
    print(f"Running {level_name}...")

    for i in range(10):
        print(f"  Run {i + 1}...")

        start = time.time()
        proc = subprocess.Popen(
            [SOLVER_PATH, "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = proc.communicate(input=level_str.encode())
        end = time.time()

        try:
            p = psutil.Process(proc.pid)
            time.sleep(0.01)  # minimaler Delay zur Sicherheit
            cpu_time = p.cpu_times().user + p.cpu_times().system
            mem_info = p.memory_info()
            memory_info = getattr(mem_info, 'peak_wset', mem_info.rss) / (1024 * 1024)
        except Exception as e:
            print(f"Fehler beim Erfassen von CPU/Mem: {e}")
            cpu_time = None
            memory_info = None

        duration = end - start
        cpu_str = f"{cpu_time:.3f}s" if cpu_time is not None else "N/A"
        mem_str = f"{memory_info:.1f}MB" if memory_info is not None else "N/A"
        print(f"    Zeit: {duration:.3f}s, CPU: {cpu_str}, Mem: {mem_str}")

        data.append({
            "Level": level_name,
            "Run": i + 1,
            "TimeSeconds": duration,
            "CPUSeconds": cpu_time,
            "MaxMemoryMB": memory_info,
            "ExitCode": proc.returncode,
            "Output": stdout.decode().strip(),
            "Error": stderr.decode().strip(),
        })

# Ergebnisse speichern
df = pd.DataFrame(data)
df.to_csv(CSV_OUTPUT, index=False)
print(f"\nCSV gespeichert als: {CSV_OUTPUT}")

# Einzelne Boxplots pro Level für Zeit, CPU und Speicher
metrics = ["TimeSeconds", "CPUSeconds", "MaxMemoryMB"]

for metric in metrics:
    for level in df["Level"].unique():
        df_level = df[df["Level"] == level]
        df_valid = df_level.dropna(subset=[metric])
        if not df_valid.empty:
            plt.figure(figsize=(6, 4))
            sns.boxplot(data=df_valid, y=metric)
            plt.title(f"{metric} für {level}")
            plt.ylabel(metric)
            plt.xlabel("")
            plt.tight_layout()

            plot_filename = RUN_DIR / f"{level}_{metric}.png"
            plt.savefig(plot_filename)
            plt.close()
            print(f"Plot gespeichert als: {plot_filename}")
        else:
            print(f"Keine gültigen Daten für {level} – {metric}, übersprungen.")

# Gemeinsame Boxplots über alle Levels
for metric in metrics:
    df_valid = df.dropna(subset=[metric])
    if not df_valid.empty:
        plt.figure(figsize=(12, 6))
        sns.boxplot(data=df_valid, x="Level", y=metric)
        plt.ylabel(metric)
        plt.xlabel("Level")
        plt.title(f"{metric} pro Level (je 10 Wiederholungen)")
        plt.xticks(rotation=45)
        plt.tight_layout()

        plot_filename = RUN_DIR / f"all_levels_{metric}.png"
        plt.savefig(plot_filename)
        plt.close()
        print(f"Gesamtplot gespeichert als: {plot_filename}")
    else:
        print(f"Kein gemeinsamer Plot für {metric} möglich – alle Werte fehlen.")
