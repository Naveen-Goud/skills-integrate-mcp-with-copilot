"""
Database utilities for backup and recovery operations.

Provides functions for backing up and restoring database data.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

from models import Activity, Participant


def backup_database(db: Session, backup_dir: str = "backups") -> str:
    """
    Create a JSON backup of the current database state.
    
    Args:
        db: Database session
        backup_dir: Directory to store backups
        
    Returns:
        Path to the created backup file
    """
    # Create backup directory if it doesn't exist
    Path(backup_dir).mkdir(exist_ok=True)
    
    # Get all activities and participants
    activities = db.query(Activity).all()
    
    backup_data = {
        "timestamp": datetime.now().isoformat(),
        "activities": []
    }
    
    for activity in activities:
        activity_dict = {
            "name": activity.name,
            "description": activity.description,
            "schedule": activity.schedule,
            "max_participants": activity.max_participants,
            "participants": [p.email for p in activity.participants]
        }
        backup_data["activities"].append(activity_dict)
    
    # Create backup file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"backup_{timestamp}.json")
    
    with open(backup_path, "w") as f:
        json.dump(backup_data, f, indent=2)
    
    print(f"Backup created: {backup_path}")
    return backup_path


def restore_database(db: Session, backup_file: str) -> None:
    """
    Restore database from a JSON backup file.
    
    WARNING: This will clear existing data and restore from backup.
    
    Args:
        db: Database session
        backup_file: Path to the backup JSON file
    """
    if not os.path.exists(backup_file):
        raise FileNotFoundError(f"Backup file not found: {backup_file}")
    
    # Load backup data
    with open(backup_file, "r") as f:
        backup_data = json.load(f)
    
    # Clear existing data
    db.query(Participant).delete()
    db.query(Activity).delete()
    
    # Restore activities and participants
    for activity_data in backup_data["activities"]:
        participants_emails = activity_data.pop("participants")
        
        activity = Activity(**activity_data)
        
        for email in participants_emails:
            participant = Participant(email=email)
            activity.participants.append(participant)
        
        db.add(activity)
    
    db.commit()
    print(f"Database restored from: {backup_file}")


def list_backups(backup_dir: str = "backups") -> list:
    """
    List all available backup files.
    
    Args:
        backup_dir: Directory containing backups
        
    Returns:
        List of backup file paths
    """
    if not os.path.exists(backup_dir):
        return []
    
    backups = sorted(Path(backup_dir).glob("backup_*.json"), reverse=True)
    return [str(b) for b in backups]
