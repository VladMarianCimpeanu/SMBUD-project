import pandas as pd
import argparse


def clean(input_file, output_file):
    df = pd.read_csv(input_file)
    replace_values = {}
    for number in range(1, 10):
        replace_values[number] = "0" + str(number)
    print(replace_values)
    df = df.replace({"codice_regione_ISTAT": replace_values})
    df.to_csv(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cleaner script. It converts 'codice_regione_ISTAT' codes of a given"
                                                 "csv file to the appropriate format.\n"
                                                 "Arguments:\n"
                                                 "--input : file to be converted\n"
                                                 "--output: destination file\n")
    parser.add_argument('--input', dest='input', default="somministrazioni-vaccini-latest.csv", help="Input file name.")
    parser.add_argument('--output', dest='output', default="cleaned_data.csv", help="Output file name.")
    args = parser.parse_args()
    clean(args.input, args.output)
