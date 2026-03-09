import os
import sys
import django
from django.db import connection

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campus_recruitment_system.settings")
django.setup()

def drop_tables():
    with connection.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                print(f"Dropped table {table_name}")
            except Exception as e:
                print(f"Error dropping {table_name}: {e}")
                
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

if __name__ == '__main__':
    drop_tables()