class NameParser:

    def parse_txt(self, filename):
        parsed_names = []
        with open(filename, encoding="utf8") as file:
            for line in file:
                parsed_names.append(line.rstrip().capitalize())
        return parsed_names

    def parse_csv(self, filename):
        parsed_names = []
        with open(filename, encoding="utf8") as file:
            for line in file:
                parsed_names.append(line.rstrip().capitalize())
        return parsed_names


if __name__ == "__main__":
    parser = NameParser()
    parsed = parser.parse_txt("cognomi.txt")
    for i in parsed:
        print(i)
