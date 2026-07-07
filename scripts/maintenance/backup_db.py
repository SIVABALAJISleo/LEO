import sqlite3
import os
from datetime import datetime

DB_PATH = "hyper_production.db"
BACKUP_DIR = "backups"

def perform_backup():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"hyper_backup_{timestamp}.db")
    
    print(f"Starting zero-downtime backup of {DB_PATH} to {backup_path}...")
    
    try:
        # Connect to existing production database
        src = sqlite3.connect(DB_PATH)
        # Connect to new backup file
        dest = sqlite3.connect(backup_path)
        
        # Use SQLite backup API
        with dest:
            src.backup(dest)
        
        dest.close()
        src.close()
        
        print(f"Backup completed successfully: {backup_path}")
        
    except Exception as e:
        print(f"Backup failed: {e}")
        if os.path.exists(backup_path):
            os.remove(backup_path)

if __name__ == "__main__":
    perform_backup()
