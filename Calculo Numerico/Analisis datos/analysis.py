# Analysis of wind data
import os
import pandas as pd
import matplotlib.pyplot as plt

RESULTS_DIR = "Results"

def main():
    print("Loading data...", end="\n\n")
    model = read_model("Data/model.txt")

    try:
        os.mkdir(RESULTS_DIR)
    except FileExistsError:
        pass

    plt.style.use("bmh")

    print("Scatter figures matrix of first 1000 records", end="\n\n")
    plot_scatter_first_1000(model)

    print("Scatter figures matrix of first 1000 records"
          " with greatest wind speed", end="\n\n")
    plot_scatter_greatest_speed_1000(model)

    print("Histogram of wind speed with 36 partitions", end="\n\n")
    plot_histogram_speed(model)

    print("Monthly history of wind mean speed", end="\n\n")
    monthly = monthly_mean_speed(model)

    print("Table of monthly wind mean speed", end="\n\n")
    monthly_table = table_from_historic(monthly)

    print("Plot of monthly wind mean speed per year", end="\n\n")
    plot_monthly_historic(monthly_table)


def plot_scatter_first_1000(model):
    # Select the first 1000 rows for "Speed(m/s)" and "Direction(deg)"
    subset = model.iloc[:1000]

    # Create a scatter_matrix plot
    pd.plotting.scatter_matrix(subset)
    #plt.title("Scatter Plots of the First 1000 Records")
    plt.show()

def plot_scatter_greatest_speed_1000(model):
    # Select the top 1000 rows with the greatest "Speed(m/s)"
    top_speeds = model.nlargest(1000, "Speed(m/s)")

    # Create a scatter_matrix plot
    pd.plotting.scatter_matrix(top_speeds)
    #plt.title("Scatter Plots of the Top 1000 Speeds")
    plt.show()

def plot_histogram_speed(model):
    # Plotting the histogram with 36 bins
    plt.hist(model["Speed(m/s)"], bins=36, alpha=0.75, edgecolor='black')

    # Adding labels and title
    plt.xlabel("Speed(m/s)")
    plt.ylabel("Frequency")
    plt.title("Histogram of Wind Speeds")

    # Display the plot
    plt.show()

def monthly_mean_speed(model):
    # Group by year and month and compute mean wind speed
    monthly = model["Speed(m/s)"].groupby([model.index.year,
                                           model.index.month]).mean()
    monthly.rename_axis(index=["Year", "Month"], inplace=True)

    # Preview and save the results
    print(monthly, end="\n\n")
    monthly.to_csv(RESULTS_DIR + "/mon_hist_wind_mean_speed.txt", "\t")

    # Plot the history
    monthly.plot(figsize=(15, 5))
    plt.ylabel("Mean Speed(m/s)")
    plt.title("Monthly History of Mean Wind Speed")
    plt.show()

    return monthly

def table_from_historic(monthly):
    # Pivot table to have years as rows and months as columns,
    # from the results of monthly_mean_speed
    pivot_table = monthly.unstack()

    # Preview and save the results
    print(pivot_table, end="\n\n")
    pivot_table.to_csv(RESULTS_DIR + "/mon_table_wind_mean_speed.txt", "\t")

    return pivot_table

def plot_monthly_historic(monthly_table):
    monthly_table = monthly_table.T

    # Plotting
    monthly_table.plot(figsize=(15, 5), linewidth=1.5)
    plt.ylabel("Mean Wind Speed (m/s)")
    plt.legend(loc="upper right", ncol=8)
    plt.title("Monthly Mean Wind Speed per Year")
    plt.show()

def read_model(path):
    model = pd.read_csv(path, sep="\s+", skiprows=3,
                        usecols=["YYYYMMDD", "HHMM", "M(m/s)", "D(deg)"],
                        parse_dates={"Timestamp": [0, 1]}, index_col="Timestamp")
    model.rename(columns={"M(m/s)": "Speed(m/s)",
                          "D(deg)": "Direction(deg)"},
                 inplace=True)
    return model

if __name__ == "__main__":
    main()

