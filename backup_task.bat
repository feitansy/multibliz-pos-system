# Windows Task Scheduler - Database Backup
# Run this script daily at 2 AM

# Save this as: backup_task.bat
@echo off
cd "C:\Users\SCATTER ONLY\Multibliz POS System"
"C:\Users\SCATTER ONLY\Multibliz POS System\.venv\Scripts\python.exe" scripts\backup_database.py backup

# To schedule this task:
# 1. Open Task Scheduler
# 2. Create Basic Task
# 3. Name: "Multibliz Database Backup"
# 4. Trigger: Daily at 2:00 AM
# 5. Action: Start a program
# 6. Program: C:\Users\SCATTER ONLY\Multibliz POS System\backup_task.bat
