import pyodbc
import streamlit as st
from datetime import datetime
from core.connection import connect_to_app_database
from core.logging import log_action

def get_all_data_people(conn, table="people"):
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        return rows
    except pyodbc.Error as e:
        st.error(f"Error retrieving data: {e}")
        return None

def insert_data(conn, username, name, age):
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO people (name, age) VALUES (?, ?)", (name, age))
        conn.commit()
        
        cursor.execute("SELECT SCOPE_IDENTITY()")
        user_id = cursor.fetchone()[0]
        
        st.success(f"Inserted '{name}' with age {age} into 'people' table")
        log_action(username, user_id, f"Inserted '{name}' with age {age}")
    except pyodbc.Error as e:
        st.error(f"Error inserting data: {e}")

def update_data(conn, username, people_id, name, age):
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE people SET name = ?, age = ? WHERE people_id = ?", (name, age, people_id))
        conn.commit()
        st.success(f"Updated user with ID {people_id} in 'people' table")
        log_action(username, people_id, f"Updated user with ID {people_id} to name '{name}' and age {age}")
    except pyodbc.Error as e:
        st.error(f"Error updating data: {e}")

def delete_data(conn, username, people_id):
    try:
        cursor = conn.cursor()

        # Check if the user exists
        cursor.execute("SELECT COUNT(*) FROM people WHERE people_id = ?", (people_id,))
        if cursor.fetchone()[0] == 0:
            st.error(f"User with ID {people_id} does not exist.")
            return
        
        # Check if there are associated logs
        cursor.execute("SELECT COUNT(*) FROM log_people WHERE people_id = ?", (people_id,))
        if cursor.fetchone()[0] > 0:
            st.error(f"Cannot delete user with ID {people_id} because there are logs associated with this user.")
            return
        
        # Delete the user
        cursor.execute("DELETE FROM people WHERE people_id = ?", (people_id,))
        conn.commit()
        st.success(f"Deleted user with ID {people_id} from 'people' table")
        log_action(username, people_id, f"Deleted user with ID {people_id}")
    except pyodbc.Error as e:
        st.error(f"Error deleting data: {e}")
