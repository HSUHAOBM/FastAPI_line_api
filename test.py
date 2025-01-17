import psycopg2

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="postgres",
    host="localhost",
    port=5432
)
print("Connected to database")
