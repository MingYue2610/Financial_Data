import pandas as pd
import csv
from datetime import datetime
import logging
from data_entry import get_amount,get_category, get_date, get_description
import matplotlib.pyplot as plt


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CSV:
    CSV_FILE= "finance_data.csv"
    COLUMNS = ["date", "amount", "category", "description"]
    FORMAT = "%d-%m-%Y"  # Ensuring the format is in the dd-mm-yyyy

    @classmethod
    def initialise_csv(cls):
        try:
            pd.read_csv(cls.CSV_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=cls.COLUMNS)
            df.to_csv(cls.CSV_FILE, index=False)
            logger.info("CSV File Created")

    @classmethod
    def add_entry(cls, date, amount, category, description):
        new_entry = {
            "date": date,
            "amount": amount,
            "category": category,
            "description": description,
        }
        with open(cls.CSV_FILE, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cls.COLUMNS)
            writer.writerow(new_entry)
        logger.info("New Entry Added Succesfully")

    @classmethod
    def get_transactions(cls, start_date, end_date): # CSV.get_transactions("01-01-2023","01-08-2024") - This is where you can see an overview of Income and Expense between a range of date
        df = pd.read_csv(cls.CSV_FILE)
        df["date"] = pd.to_datetime(df["date"], format=CSV.FORMAT) #Converting the date from str to DateTime object
        start_date = datetime.strptime(start_date,CSV.FORMAT)
        end_date = datetime.strptime(end_date, CSV.FORMAT)

        mask = (df["date"] >= start_date) & (df["date"] <= end_date) #Because we coverted the start/end date into DateTime object, this allow us to perform comparison within these range
        filtered_df = df.loc[mask]

        if filtered_df.empty:
            print("No transaction found in the given date range")
        else:
            print(f"Transactions from {start_date.strftime(CSV.FORMAT)} to {end_date.strftime(CSV.FORMAT)}") #Using our datetime objects to be outputted as a string using a f string
            print(filtered_df.to_string(index=False, formatters={"date": lambda x: x.strftime(CSV.FORMAT)})) #One line anonymous lambda function

            total_income = filtered_df[filtered_df["category"] == "Income"]["amount"].sum() #Looking through the filter column that matches Income then find the total amount
            total_expense = filtered_df[filtered_df["category"] == "Expense"]["amount"].sum()
            print("\nSummary:")
            print(f"Total Income: ${total_income:.2f}")
            print(f"Total Expense: ${total_expense:.2f}")
            print(f"Net Savings: ${(total_income - total_expense):.2f}")
        return filtered_df

def add():
    CSV.initialise_csv()
    date = get_date("Enter the date of the transaction (dd-mm-yyyy) or press enter for today's date: ", allow_default=True)
    amount = get_amount()
    category = get_category()
    description = get_description()
    CSV.add_entry(date,amount,category,description)

def plot_transactions(df):
    df.set_index("date", inplace=True) #We modify the df inplace so that we can plot using the date to find different rows using the date column

    income_df = df[df["category"] == "Income"].resample("D").sum().reindex(df.index, fill_value=0) #This bit adds index value to when income is zero so that they can plot a smooth line instead of random coordinates
    expense_df = df[df["category"] == "Expense"].resample("D").sum().reindex(df.index, fill_value=0)

    plt.figure(figsize=(10,5))
    plt.plot(income_df.index, income_df["amount"], label="Income", color="g")
    plt.plot(expense_df.index, expense_df["amount"], label="Expense", color="r")
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.title("Income and Expense Over Time")
    plt.legend()
    plt.grid(True)
    plt.show()

def main():
    while True:
        print("\n1. Add a new transaction")
        print("2. View transactions and summary within a date range")
        print("3. Exit")
        choice = input("Enter your choice (1-3): ")

        if choice == "1":
            add() # Call upon this function to add new entry to the csv file
        elif choice == "2":
            start_date = get_date("Enter the start date (dd-mm-yyyy): ")
            end_date = get_date("Enter the end date (dd-mm-yyyy): ")
            df = CSV.get_transactions(start_date,end_date)
            if input("Do you want to see a plot? (y/n) ").lower() == "y":
                plot_transactions(df)
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Enter 1, 2 or 3.")
if __name__ == "__main__":
    main()