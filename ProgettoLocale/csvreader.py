import csv

# Define the path to your CSV file
csv_file_path = '/Users/albi/Desktop/Università/tirocinio_chiese/fileExcel/Chiese.CSV'

# Open the CSV file in read mode
with open(csv_file_path, 'r', encoding='latin-1') as file:
    # Create a CSV reader object
    csv_reader = csv.reader(file)
    # Iterate over each row in the CSV file
    for row in csv_reader:
        # Process each row as needed
        print(row)
