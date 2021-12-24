import pandas as pd

df = pd.read_csv("somministrazioni-vaccini-latest.csv")
replace_values = {}
for number in range(1, 10):
    replace_values[number] = "0" + str(number)
print(replace_values)
df = df.replace({"codice_regione_ISTAT": replace_values})
df.to_csv("cleaned_data.csv")
