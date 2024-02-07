import sqlite3 as sql
import csv

######SOME HELPFUL FILES FOR USING SQL in CSCA20
######Copyright Brian Harrington, 2022
######
######csv_to_table - read a csv file into an sql table
######table_to_csv - output a sql table to a csv file
######select_to_csv - output results of a select statement to a csv file
######print_table - print the details of a sql table
######table to csv - output a sql table to a csv file


def csv_to_table(db_handle, csv_handle, table_name, types):
    """
    INPUTS:
    db_handle - a link to an open sqlite3 database
    csv_handle - a link to a csv formatted file open for reading
    table_name - a string giving hte name of the table to create
    types - a list of the types of the fields in the table (must
        correspond to the order of the fields in the csv file)

    Create a table with the data in csv_handle, the names of the
    fields will be taken from the headers of the csv file, and the
    types from the types list
    """

    csv_reader = csv.reader(csv_handle)
    headers = next(csv_reader)
    cur = db_handle.cursor()
    #lets drop the old table if one exists (careful, this means we will overwrite)
    cur.execute("DROP TABLE IF EXISTS " + table_name)
    create_command = "CREATE TABLE " + table_name + "("
    for i in range(0, len(headers),1):
        #headers may have spaces, we need to replace them
        column_name = headers[i].replace(" ", "_")
        create_command += column_name + " " + types[i]
        #we want to add a comma afer all the headers except the last one
        if(i < len(headers)-1):
            create_command += ","
        else:
            create_command += ")"
    # print(create_command) #<--uncomment to see the create command
    #we've made our command to build our table, now we need to execute it
    cur.execute(create_command)

    #now let's loop through the file adding the data to the table one row at a time
    for next_row in csv_reader:
        insert_command = "INSERT INTO " + table_name + " VALUES ("
        #we need to add as many spaces as there are columns
        #instead of looping twice we can build both strings at once and combine them
        for i in range(0, len(next_row), 1):
            #if we're doing a TEXT input, we need to add single quotes around it
            if(types[i] == "TEXT"):
                insert_command += "'" + next_row[i] + "'"
            else:
                insert_command += next_row[i]

            #we want to add a comma after all the values except the last one
            if(i < len(next_row) -1):
                insert_command += ","
            else:
                insert_command += ")"
        #print(insert_command) #<-- uncomment to see the insert commands
        cur.execute(insert_command)
    #before we leave, we should commit our chages and close our cursor
    db_handle.commit()
    cur.close()

def table_to_csv(db_handle, file_handle, table_name):
    """
    INPUTS:
    db_handle - a link to an open sqlite3 database
    file_handle - a link to a file open for writing
    table_name - the name of the table to write to the CSV file
    
    Write the contents of table_name to a properly formatted CSV file
    the headers of the CSV file will be taken from the field names of
    the table
    """
    csv_writer = csv.writer(file_handle)
    cur = db_handle.cursor()
    cur.execute("SELECT * FROM " + table_name)
    #get the names of each field in the table
    headers = []
    for fields in cur.description:
        headers.append(fields[0])
    csv_writer.writerow(headers)
    for record in cur:
        csv_writer.writerow(record)
    cur.close()
    
def select_to_csv(db_handle, file_handle, select_string):
    """
    INPUTS:
    db_handle - a link to an open sqlite3 database
    file_handle - a link to a file open for writing
    select_string - a properly formatted SQL SELECT statement
    
    Execute the SELECT statement, and write the results to a csv file
    """
    csv_writer = csv.writer(file_handle)
    cur = db_handle.cursor()
    cur.execute(select_string)
    #get the names of each field in the table
    headers = []
    for fields in cur.description:
        headers.append(fields[0])
    csv_writer.writerow(headers)
    for record in cur:
        csv_writer.writerow(record)
    cur.close()

def print_table(db_handle, table_name):
    """
    Just a nice helper function to print the contents of a table in
    a relatively easy to read manner
    """
    cur = db_handle.cursor()
    cur.execute("SELECT * FROM " + table_name)
    #get the names of each field in the table
    print("TABLE: " + table_name)
    header_line = ""
    for fields in cur.description:
        header_line += fields[0] + "\t"
    print(header_line)
    for record in cur:
        next_line = ""
        for next_field in record:
            next_line += str(next_field) + "\t"
        print(next_line)
        
def print_select(db_handle, select_string):
    """
    Just a nice helper function to print the results of a select statement in
    a relatively easy to read manner
    """
    cur = db_handle.cursor()
    cur.execute(select_string)
    print("RESULT: " + select_string)
    #get the names of each field in the table
    headers_line = ""
    for fields in cur.description:
        headers_line += fields[0] + "\t"
    print(headers_line)

    # modified code below to make sure my loop only begins if has_records = True
    # initialized has_records = False
    has_records = False
    for record in cur:
        has_records = True
        next_line = ""
        for field in record:
            next_line += str(field) + "\t"
        print(next_line)
    cur.close()
    return has_records


