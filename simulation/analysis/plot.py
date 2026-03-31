import pandas as pd
import matplotlib.pyplot as plt

# Load CSV data
file = "runs.csv"
df = pd.read_csv(file)

# Plot throttle per run
plt.figure()
plt.plot(df["run_id"], df["throttle"], marker='o')
plt.title("Throttle at Detection per Run")
plt.xlabel("Run ID")
plt.ylabel("Throttle")
plt.grid()

# Optional: histogram
plt.figure()
plt.hist(df["throttle"], bins=10)
plt.title("Throttle Distribution")
plt.xlabel("Throttle")
plt.ylabel("Frequency")

plt.show()
