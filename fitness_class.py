# Import necessary modules
import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

# Run these codes to install library in terminal:
# pip install sqlalchemy
# python -m tkinter     

# Database connection details
engine = create_engine('sqlite:///fitness_classes.db', echo=True)
SessionLocal = sessionmaker(autoflush=False, bind=engine)
Base = declarative_base()

# Define database models
class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True)
    name = Column(String , unique=True)
    reservations = relationship("Reservation", backref="member")

class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    day = Column(String)
    time = Column(String)
    capacity = Column(Integer)

    __table_args__ = (
        CheckConstraint("id <= 21", name="check_max_classes"),  # Constraint for class ID
    )

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey("members.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))

# Create tables in the database
Base.metadata.create_all(engine)

# Function to populate classes in the database
def create_classes():
    session = SessionLocal()

    # Define days of the week and time slots
    days = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    time_slots = ["8:00 - 10:00", "10:00 - 12:00", "12:00 - 14:00"]

    # Define class names
    class_names = ["Basketball", "Soccer", "Tennis", "Volleyball", "Swimming", "Martial", "Gymnastics", 
                    "Track", "Cycling", "Yoga", "Golf", "Rugby", "Cricket", "Badminton", "Boxing", 
                    "Dance", "Ultimate", "Ice", "Snowboarding", "Water", "Archery"]

    for day in days:
        for time_slot in time_slots:
            class_name = class_names.pop(0) if class_names else "Generic Class"
            start_time = time_slot.split(' - ')[0]  # Extract start time from the time slot
            capacity = 10  # Set the capacity for each class

            # Check if a class with the same name already exists
            existing_class = session.query(Class).filter_by(name=class_name).first()
            if existing_class:
                continue  # Skip adding the class if it already exists

            new_class = Class(name=class_name, day=day, time=start_time, capacity=capacity)
            session.add(new_class)

    session.commit()
    session.close()

# Call the function to populate classes
create_classes()

# Function to handle login window
def login_window():
    # Function to handle login action
    def login():
        global current_member 
        member_name = entry.get()
        session = SessionLocal()
        member = session.query(Member).filter_by(name=member_name).first()
        session.close()
        if not member:
            messagebox.showerror("Error", "Member not found.")
        else:
            current_member = member  
            window.destroy()  
            schedule_window()  

    # Function to handle becoming a member action
    def become_member():
        new_member_name = entry.get()
        if new_member_name:
            session = SessionLocal()
            existing_member = session.query(Member).filter_by(name=new_member_name).first()
            if existing_member:
                messagebox.showerror("Error", "A member with the same name already exists.")
            else:
                new_member = Member(name=new_member_name)
                session.add(new_member)
                session.commit()
                session.close()
                messagebox.showinfo("Success", "New member added successfully.")
        else:
            messagebox.showerror("Error", "Please enter a name for the new member.")

    # Create the login window
    window = tk.Tk()
    window.title("Login")

    # Add label and entry for member name input
    label = ttk.Label(window, text="Enter your member name:")
    label.pack()
    entry = ttk.Entry(window)
    entry.pack()

    # Add login and become member buttons
    login_button = ttk.Button(window, text="Login", command=login)
    login_button.pack()
    new_member_button = ttk.Button(window, text="Become a Member", command=become_member)
    new_member_button.pack()

    window.mainloop()

# Function to handle the schedule window
def schedule_window():
    session = SessionLocal()

    # Function to handle reserving or canceling a class
    def reserve_or_cancel_class(class_id, reserve_button):
        selected_class = session.query(Class).filter_by(id=class_id).first()
        if selected_class:
            existing_reservation = session.query(Reservation).filter_by(member_id=current_member.id, class_id=class_id).first()
            if existing_reservation:
                session.delete(existing_reservation)
                session.commit()
                reserve_button.config(text="Reserve")
                messagebox.showinfo("Success", "Reservation canceled.")
            else:
                reservations_count = session.query(Reservation).filter_by(class_id=class_id).count()
                if reservations_count >= selected_class.capacity:
                    messagebox.showerror("Error", "Class is already full.")
                else:
                    new_reservation = Reservation(member_id=current_member.id, class_id=class_id)
                    session.add(new_reservation)
                    session.commit()
                    reserve_button.config(text="Cancel")
                    messagebox.showinfo("Success", "Reservation successful.")
        else:
            messagebox.showerror("Error", "Class not found.")

    # Function to view members of a class
    def view_members(class_id):
        selected_class = session.query(Class).filter_by(id=class_id).first()
        if selected_class:
            reservations = session.query(Reservation).filter_by(class_id=class_id).all()
            member_list = [reservation.member.name for reservation in reservations]
            if member_list:
                messagebox.showinfo("Class Members", ", ".join(member_list))
            else:
                messagebox.showinfo("Class Members", "No members have reserved this class yet.")
        else:
            messagebox.showerror("Error", "Class not found.")

    # Function to handle logout action
    def logout():
        global current_member
        current_member = None
        window.destroy()
        login_window()

    # Create the schedule window
    window = tk.Tk()
    window.title("Class Schedule")

    # Define days of the week and time slots
    days = ("Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday")
    time_slots = ["8:00 - 10:00", "10:00 - 12:00", "12:00 - 14:00"]

    # Loop through time slots and days to display class schedule
    for i, day in enumerate(days):
        label = ttk.Label(window, text=day)
        label.grid(row=0, column=i + 1, padx=10, pady=10)

    for i, time_slot        in enumerate(time_slots):
        label = ttk.Label(window, text=time_slot)
        label.grid(row=i + 1, column=0, padx=10, pady=10)

        for j, day in enumerate(days):
            class_id = i * len(days) + j + 1
            selected_class = session.query(Class).filter_by(day=day, time=time_slot.split(' - ')[0]).first()
            class_name = selected_class.name if selected_class else "No class"

            class_label = ttk.Label(window, text=class_name)
            class_label.grid(row=i + 1, column=j + 1, padx=10, pady=60)

            # Button to view members of the class
            view_button = ttk.Button(window, text="View Members", width=20, command=lambda id=class_id: view_members(id))
            view_button.grid(row=i + 1, column=j + 1, sticky="sw", padx=10, pady=30)

            # Button to reserve or cancel the class
            reserve_button_text = "Cancel" if session.query(Reservation).filter_by(member_id=current_member.id, class_id=class_id).first() else "Reserve"
            reserve_button = ttk.Button(window, text=reserve_button_text, width=20)
            reserve_button.grid(row=i + 1, column=j + 1, sticky="se", padx=10, pady=5)
            reserve_button.configure(command=lambda id=class_id, button=reserve_button: reserve_or_cancel_class(id, button))

    # Add logout button
    logout_button = ttk.Button(window, text="Logout", command=logout)
    logout_button.grid(row=len(time_slots) + 2, column=0, columnspan=len(days) + 1, padx=5, pady=5)

    window.mainloop()

# Start the login window
login_window()

