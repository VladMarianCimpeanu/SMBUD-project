import pandas as pd

file = pd.read_csv("addresses.csv")
file.loc[file['municipality'] == "Roma"].to_csv('rome.csv')
file.loc[file['municipality'] == "Napoli"].to_csv('naples.csv')
file.loc[file['municipality'] == "Milano"].to_csv("milan.csv")


