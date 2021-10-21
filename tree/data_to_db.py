import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="tree",
    user="postgres",
    password="postgres")

cursor = conn.cursor()

cursor.execute("select * from tree_course")
courses = cursor.fetchall()
print(courses)
