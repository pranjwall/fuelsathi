import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('instance/fuelsathi.db')
cursor = conn.cursor()

# Execute query to select all users
cursor.execute('SELECT * FROM user')
rows = cursor.fetchall()

# Print the results
print('Users in the database:')
for row in rows:
    print(row)

# Close the connection
conn.close()
