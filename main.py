import subprocess
import time
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
from datetime import datetime

# Pfad zum Ordner mit Level-Dateien
LEVEL_DIR = Path(r"C:\Users\florian.widhalm\Documents\BA\hexSolverASCII\extra")
SOLVER_PATH = r"C:\Users\florian.widhalm\Documents\BA\hexSolverASCII\target\debug\hexcells-solver.exe"

# Basisverzeichnis (dort, wo das Skript liegt)
SCRIPT_DIR = Path(__file__).parent.resolve()

# Zeitstempel im Format HHMMDDMMYY
timestamp = datetime.now().strftime("%H%M%d%m%y")

# Neuer Ordner für diesen Lauf
RUN_DIR = SCRIPT_DIR / "solver_runs" / timestamp
RUN_DIR.mkdir(parents=True, exist_ok=True)

CSV_OUTPUT = RUN_DIR / "solver_times.csv"

# Alle .txt-Dateien im Level-Verzeichnis finden
level_files = sorted(LEVEL_DIR.glob("*.txt"))

data = []

for level_file in level_files:
    with open(level_file, "r") as f:
        level_str = f.read()

    level_name = level_file.stem
    print(f"Running {level_name}...")

    for i in range(10):
        start = time.time()
        proc = subprocess.run(
            [SOLVER_PATH, "-"],
            input=level_str.encode(),
            capture_output=True,
        )
        end = time.time()
        duration = end - start
        data.append({
            "Level": level_name,
            "Run": i + 1,
            "TimeSeconds": duration,
            "ExitCode": proc.returncode,
            "Output": proc.stdout.decode().strip(),
            "Error": proc.stderr.decode().strip(),
        })
        print(f"  Run {i + 1}: {duration:.3f}s")

# Als DataFrame speichern
df = pd.DataFrame(data)

# CSV-Datei speichern
df.to_csv(CSV_OUTPUT, index=False)
print(f"\nCSV gespeichert als: {CSV_OUTPUT}")

# Einzelne Boxplots pro Level erzeugen
unique_levels = df["Level"].unique()

for level in unique_levels:
    df_level = df[df["Level"] == level]
    plt.figure(figsize=(6, 4))
    sns.boxplot(data=df_level, y="TimeSeconds")
    plt.title(f"Laufzeiten für {level}")
    plt.ylabel("Laufzeit (Sekunden)")
    plt.xlabel("")
    plt.tight_layout()

    plot_filename = RUN_DIR / f"{level}.png"
    plt.savefig(plot_filename)
    plt.close()
    print(f"Plot gespeichert als: {plot_filename}")

# Gemeinsamer Boxplot für alle Levels
plt.figure(figsize=(12, 6))
sns.boxplot(data=df, x="Level", y="TimeSeconds")
plt.ylabel("Laufzeit (Sekunden)")
plt.xlabel("Level")
plt.title("Solver-Laufzeiten pro Level (je 10 Wiederholungen)")
plt.xticks(rotation=45)
plt.tight_layout()

combined_plot_filename = RUN_DIR / "all_levels.png"
plt.savefig(combined_plot_filename)
plt.close()
print(f"\nGesamtplot gespeichert als: {combined_plot_filename}")
