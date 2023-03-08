import csv

def csv_create(column_list, dict_data, csv_filename):
    csv_columns = column_list
    dictionary_data = dict_data
    csv_file = ("{}.csv".format(csv_filename))

    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for row in dictionary_data:
                writer.writerow(row)
    except IOError:
        print("I/O Error")

    return csv_file