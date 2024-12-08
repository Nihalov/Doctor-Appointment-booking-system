import psycopg2
import json
# Establish the connection
def connect_to_db():
    return psycopg2.connect(
        dbname="doctorAppointmentDb",
        user="postgres",
        password="Superuser@123",
        host="localhost",
        port= "5432"
    )
    

connect_to_db()#fn call to connect db