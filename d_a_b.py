import json
import psycopg2
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

# Establish the connection
def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname="doctorAppointmentDb",
            user="postgres",
            password="Superuser@123",
            host="localhost",
            port= "5432"
        )
    except Exception as e:
        print(f"Database connection incomplete:{e}")
        return None
    
    cursor = conn.cursor()
    
    #create doctors table
    cursor.execute("""create table if not exists doctors(
	id serial primary key,
	name varchar(100) not null,
	availability jsonb,
	specialization varchar(200) not null,
	contact varchar(15)
	)
    """)
    
    
    #create patients table
    cursor.execute("""create table if not exists patients(
	id serial primary key,
	name varchar(200) not null,
	age varchar(50) not null,
	contact varchar(15) not null,
    gender varchar(20)
	)
    """)
    
    #create appointments table
    cursor.execute("""create table if not exists appointments(
	id serial primary key,
	patient_id int references patients(id) on delete cascade,
	doctor_id int references doctors(id) on delete cascade,
	date date not null,
	time time without time zone,
	unique(patient_id, doctor_id, date, time)
    )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM doctors")
    doctor_count = cursor.fetchone()[0]
    if doctor_count == 0:
        cursor.execute("ALTER SEQUENCE doctors_id_seq RESTART WITH 1")
        
    cursor.execute("SELECT COUNT(*) FROM patients")
    patient_count = cursor.fetchone()[0]
    if patient_count == 0:
        cursor.execute("ALTER SEQUENCE patients_id_seq RESTART WITH 1")

    cursor.execute("SELECT COUNT(*) FROM appointments")
    appointment_count = cursor.fetchone()[0]
    if appointment_count == 0:
        cursor.execute("ALTER SEQUENCE appointments_id_seq RESTART WITH 1")

    return conn


def add_doc(name,availability,specialization,contact):
    conn=connect_to_db()
    if conn:
        try:
            cursor=conn.cursor()
            cursor.execute(
                """INSERT INTO doctors(name,availability,specialization,contact)VALUES(%s,%s,%s,%s)""",
                (name,json.dumps(availability),specialization,contact)
            )
            conn.commit()
            messagebox.showinfo("Succeeded","Doctor info added successfully.")
        except Exception as e:
            messagebox.showerror("Failed",f"Doctor info cannot be added:{e}")
        finally:
            cursor.close()
            conn.close()
            

def add_patient(name, age, contact, gender):
    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO patients(name, age, contact, gender) VALUES(%s, %s, %s, %s)""",
                (name, age, contact, gender)
            )
            conn.commit()
            messagebox.showinfo("Succeeded", "Patient info added successfully.")
        except Exception as e:
            messagebox.showerror("Failed", f"Patient info cannot be added: {e}")
        finally:
            cursor.close()
            conn.close()


def book_appointment(patient_id, doctor_id, date, time):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        
        date = datetime.strptime(date, "%Y-%m-%d").date()
        time = datetime.strptime(time, "%H:%M").time()
        
        appointment_datetime = datetime.combine(date, time)

        lower_bound = appointment_datetime - timedelta(minutes=10)
        upper_bound = appointment_datetime + timedelta(minutes=10)

        # Check if there's an existing appointment for the same doctor within 10 minutes of the requested time
        cursor.execute("""
            SELECT COUNT(*) FROM appointments 
            WHERE doctor_id = %s 
            AND date = %s 
            AND time BETWEEN %s AND %s
        """, (doctor_id, date, lower_bound.time(), upper_bound.time()))
        
        # If there is an appointment in the range,cannot book
        if cursor.fetchone()[0] > 0:
            cursor.close()
            conn.close()
            return False
        
        
        cursor.execute("""insert into appointments(patient_id, doctor_id, date, time) values (%s, %s, %s, %s)""",
                    (patient_id, doctor_id, date, time))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except psycopg2.errors.UniqueViolation:
        return False

def fetch_all_doctors():
    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""select * from doctors""")
            rows = cursor.fetchall()   # 'rows' will be a list containg each rows as tuples(tuple inside a list)
        except Exception as e:
            messagebox.showerror("Failed to fetch doctors")
        finally:
            cursor.close()
            conn.close()
            return rows

def fetch_all_patients():
    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""select * from patients""")
            rows = cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Failed to fetch patients")
        finally:
            cursor.close()
            conn.close()
            return rows

def fetch_all_appointments():
    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.id, p.name AS patient_name, d.name AS doctor_name, a.date, a.time 
                FROM appointments a
                JOIN patients p ON a.patient_id = p.id
                JOIN doctors d ON a.doctor_id = d.id
                ORDER BY a.date, a.time
            """)
            rows = cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Failed to fetch appointments")
            rows = []
        finally:
            cursor.close()
            conn.close()
            return rows
        

def add_doc_gui():
    def submit():
        name=name_entry.get()
        availability=availability_entry.get()
        specialization=specialization_entry.get()
        contact=contact_entry.get()
        if name and availability and specialization and contact:
            add_doc(name,availability,specialization,contact)
        else:
            messagebox.showwarning("Warning","Enter complete info.")
            
    doc_window = tk.Toplevel(root)
    doc_window.configure(bg="#f0f8ff")
    doc_window.title("Add Doctor Info")

    tk.Label(doc_window,text="Doctor Name").grid(row=0,column=0,padx=10,pady=5)
    name_entry=tk.Entry(doc_window)
    name_entry.grid(row=0,column=1,padx=10,pady=5)

    tk.Label(doc_window,text="Availablity of Doctor").grid(row=1,column=0,padx=10,pady=5)
    availability_entry=tk.Entry(doc_window)
    availability_entry.grid(row=1,column=1,padx=10,pady=5)

    tk.Label(doc_window,text="Specialization").grid(row=2,column=0,padx=10,pady=5)
    specialization_entry=tk.Entry(doc_window)
    specialization_entry.grid(row=2,column=1,padx=10,pady=5)

    tk.Label(doc_window,text="Contact").grid(row=3,column=0,padx=10,pady=5)
    contact_entry=tk.Entry(doc_window)
    contact_entry.grid(row=3,column=1,padx=10,pady=5)

    tk.Button(doc_window,text="Add Doctor Info",command=submit).grid(row=4,column=0,columnspan=2,pady=10)


def add_patient_gui():
    def submit():
        name = name_entry.get()
        age = age_entry.get()
        contact = contact_entry.get()
        gender = gender_entry.get()

        if  name and age and contact and gender:
            try:
                age = int(age)  # Ensure age is a valid integer
                if len(contact) == 10 and contact.isdigit():
                    add_patient(name, age, contact, gender)
                else:
                    messagebox.showwarning("Warning", "Contact number must be 10 digits.")
            except ValueError:
                messagebox.showwarning("Warning", "Age must be a number.")
        else:
            messagebox.showwarning("Warning", "Enter complete info.")

    patient_window = tk.Toplevel(root)
    patient_window.configure(bg="#f0f8ff")
    patient_window.title("Add Patient Info")

    tk.Label(patient_window, text="Patient Name").grid(row=1, column=0, padx=10, pady=5)
    name_entry = tk.Entry(patient_window)
    name_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(patient_window, text="Patient Age").grid(row=2, column=0, padx=10, pady=5)
    age_entry = tk.Entry(patient_window)
    age_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(patient_window, text="Contact").grid(row=3, column=0, padx=10, pady=5)
    contact_entry = tk.Entry(patient_window)
    contact_entry.grid(row=3, column=1, padx=0, pady=5)
    
    
    gender_entry = tk.StringVar(value="")
    tk.Label(patient_window, text="Gender").grid(row=4, column=0, padx=10, pady=5)
    radio1 = tk.Radiobutton(patient_window, text="Male", variable=gender_entry, value="Male")
    radio2 = tk.Radiobutton(patient_window, text="Female", variable=gender_entry, value="Female")
    
    radio3 = tk.Radiobutton(patient_window, text="Others", variable=gender_entry, value="Others")
    radio1.grid(row=4, column=1)
    radio3.grid(row=4, column=3)
    radio2.grid(row=4, column=2)

    tk.Button(patient_window, text="Add Patient Info", command=submit).grid(row=5, column=0, columnspan=2, pady=10)



def book_appointment_gui():
    def submit_appointment():
        patient = patient_var.get()
        doctor = doctor_var.get()
        date = appointment_date.get()
        time = appointment_time.get()

        if patient and doctor and date and time:
            patient_id = [p[0] for p in patients if p[1]==patient][0]
            doctor_id = [d[0] for d in doctors if d[1]==doctor][0]
            success = book_appointment(patient_id, doctor_id, date, time)
            if success:
                messagebox.showinfo("Success", "Appointment booked successfully")
                appointment_window.destroy()
            else:
                messagebox.showerror("Error", "The doctor is not available at the selected time. Please choose another time.")
        else:
            messagebox.showerror("Error", "Please fill all fields")
            
    appointment_window = tk.Toplevel(root)
    appointment_window.title("Book Appointment")
    appointment_window.configure(bg="#f0f8ff")

    doctors = fetch_all_doctors()
    patients = fetch_all_patients()
    if doctors:
        tk.Label(appointment_window, text="Doctors: ").grid(row=0, column=0)
        doctor_var = tk.StringVar()
        doctor_var.set("Select a doctor")
        doctor_menu = tk.OptionMenu(appointment_window, doctor_var, *[d[1] for d in doctors]) #d[1] is used to get 'name' column of db
        doctor_menu.grid(row=0, column=1, padx=10, pady=10)
        
        if patients:
            tk.Label(appointment_window, text="Patients: ").grid(row=1, column=0)
            patient_var = tk.StringVar()
            patient_var.set("Select a Patient")
            patient_menu = tk.OptionMenu(appointment_window, patient_var, *[p[1] for p in patients])
            patient_menu.grid(row=1, column=1, padx=10, pady=10)
        else:
            tk.Label(appointment_window, text="No Patients registered")
        
        tk.Label(appointment_window, text="Date (YYYY-MM-DD): ").grid(row=2,column=0, pady=10, padx=10)
        appointment_date = tk.Entry(appointment_window)
        appointment_date.grid(row=2, column=1, pady=10, padx=10)
        
        tk.Label(appointment_window, text="Time (HH:MM): ").grid(row=3, column=0, pady=10, padx=10)
        appointment_time = tk.Entry(appointment_window)
        appointment_time.grid(row=3, column=1, padx=10, pady=10)
        tk.Button(appointment_window, text="Submit", command=submit_appointment).grid(row=4, columnspan=2, pady=10)
        
    else:
        tk.Label(appointment_window, text="No doctors available at the moment!").grid(row=0, column=0)




def view_doctors_gui():
    doctors = fetch_all_doctors()
    if not doctors:
        messagebox.showinfo("No Data", "No doctors found.")
        return

    view_window = tk.Toplevel(root)
    view_window.title("View Doctors")
    
    tk.Label(view_window, text="ID", width=5, relief="solid").grid(row=0, column=0)
    tk.Label(view_window, text="Name", width=20, relief="solid").grid(row=0, column=1)
    tk.Label(view_window, text="Specialization", width=20, relief="solid").grid(row=0, column=2)
    tk.Label(view_window, text="Contact", width=15, relief="solid").grid(row=0, column=3)
    tk.Label(view_window, text="Availability", width=30, relief="solid").grid(row=0, column=4)
    
    for idx, doc in enumerate(doctors, start=1):
        tk.Label(view_window, text=doc[0], width=5, relief="solid").grid(row=idx, column=0)
        tk.Label(view_window, text=doc[1], width=20, relief="solid").grid(row=idx, column=1)
        tk.Label(view_window, text=doc[3], width=20, relief="solid").grid(row=idx, column=2)
        tk.Label(view_window, text=doc[4], width=15, relief="solid").grid(row=idx, column=3)
        tk.Label(view_window, text=doc[2], width=30, relief="solid").grid(row=idx, column=4)

def view_appointments_gui():
    appointments = fetch_all_appointments()
    if not appointments:
        messagebox.showinfo("No Data", "No appointments found.")
        return

    view_window = tk.Toplevel(root)

    view_window.title("View Appointments")
    
    tk.Label(view_window, text="ID", width=5, relief="solid").grid(row=0, column=0)
    tk.Label(view_window, text="Patient Name", width=20, relief="solid").grid(row=0, column=1)
    tk.Label(view_window, text="Doctor Name", width=20, relief="solid").grid(row=0, column=2)
    tk.Label(view_window, text="Date", width=15, relief="solid").grid(row=0, column=3)
    tk.Label(view_window, text="Time", width=10, relief="solid").grid(row=0, column=4)
    
    for idx, appt in enumerate(appointments, start=1):
        tk.Label(view_window, text=appt[0], width=5, relief="solid").grid(row=idx, column=0)
        tk.Label(view_window, text=appt[1], width=20, relief="solid").grid(row=idx, column=1)
        tk.Label(view_window, text=appt[2], width=20, relief="solid").grid(row=idx, column=2)
        tk.Label(view_window, text=appt[3], width=15, relief="solid").grid(row=idx, column=3)
        tk.Label(view_window, text=appt[4], width=10, relief="solid").grid(row=idx, column=4)


def setup_main_gui():
    root.title("Doctor Appointment Booking System")
    root.geometry("500x500")
    root.configure(bg="#f0f8ff")

    title_label = tk.Label(root, text="Doctor Appointment System", font=("Arial", 20, "bold"), bg="#f0f8ff", fg="#2c3e50")
    title_label.pack(pady=20)

    button_frame = tk.Frame(root, bg="#f0f8ff")
    button_frame.pack(pady=10)

    button_style = {
        "font": ("Arial", 12, "bold"),
        "bg": "#3498db",
        "fg": "white",
        "activebackground": "#2980b9",
        "activeforeground": "white",
        "relief": "raised",
        "bd": 3,
        "width": 20,
        "height": 2,
    }

    tk.Button(button_frame, text="Add Doctor", command=add_doc_gui, **button_style).pack(pady=10)
    tk.Button(button_frame, text="Add Patient", command=add_patient_gui, **button_style).pack(pady=10)
    tk.Button(button_frame, text="Book Appointment", command=book_appointment_gui, **button_style).pack(pady=10)
    tk.Button(button_frame, text="View Doctors", command=view_doctors_gui, **button_style).pack(pady=10)
    tk.Button(button_frame, text="View Appointments", command=view_appointments_gui, **button_style).pack(pady=10)



root = tk.Tk()
setup_main_gui()
root.mainloop()