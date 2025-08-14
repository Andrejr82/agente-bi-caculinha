import os
from dotenv import load_dotenv
from core.database import sql_server_auth_db as auth_db
import bcrypt

# Load environment variables from .env file
load_dotenv()

# --- Initialize the database (create table if not exists) ---
print("Initializing database...")
try:
    auth_db.init_db()
    print("Database initialized successfully. 'usuarios' table ensured.")
except Exception as e:
    print(f"Error initializing database: {e}")
    print("Please ensure your SQL Server is running and accessible, and .env variables are correct.")
    exit()

# --- Create initial admin user ---
admin_username = "admin"
admin_password = "admin123" # Default password for initial setup

print(f"Attempting to create initial admin user: {admin_username}")
try:
    auth_db.criar_usuario(admin_username, admin_password, "admin")
    print(f"Admin user '{admin_username}' created successfully with password '{admin_password}'.")
    print("Please change this password after your first login for security reasons.")
except ValueError as e:
    if "Usuário já existe" in str(e):
        print(f"Admin user '{admin_username}' already exists. Skipping creation.")
    else:
        print(f"Error creating admin user: {e}")
except Exception as e:
    print(f"An unexpected error occurred while creating admin user: {e}")

print("\nSetup complete. You can now run the Streamlit application.")
