import pandas as pd


def analyze(file="../data/runs.csv"):
    df = pd.read_csv(file)

    avg = df["throttle"].mean()
    std = df["throttle"].std()
    min_v = df["throttle"].min()
    max_v = df["throttle"].max()

    print(f"Runs: {len(df)}")
    print(f"Average: {avg:.3f}")
    print(f"Std Dev: {std:.3f}")
    print(f"Min: {min_v:.3f}")
    print(f"Max: {max_v:.3f}")

    if std < 0.02:
        print("Stable system")
    else:
        print("Unstable system")


if __name__ == "__main__":
    analyze()
