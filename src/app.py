"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.

Uses persistent database storage to ensure data survives application restarts.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import os
from pathlib import Path

from database import init_db, get_db, engine
from models import Activity, Participant, Base

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


# Initialize database on startup
@app.on_event("startup")
def startup_event():
    """Initialize the database when the application starts"""
    init_db()
    # Load sample data if database is empty
    db = next(get_db())
    try:
        if db.query(Activity).count() == 0:
            _load_sample_data(db)
    finally:
        db.close()


def _load_sample_data(db: Session):
    """Load sample activities and participants into the database"""
    sample_activities = [
        {
            "name": "Chess Club",
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        {
            "name": "Programming Class",
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        {
            "name": "Gym Class",
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        {
            "name": "Soccer Team",
            "description": "Join the school soccer team and compete in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["liam@mergington.edu", "noah@mergington.edu"]
        },
        {
            "name": "Basketball Team",
            "description": "Practice and play basketball with the school team",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["ava@mergington.edu", "mia@mergington.edu"]
        },
        {
            "name": "Art Club",
            "description": "Explore your creativity through painting and drawing",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
        },
        {
            "name": "Drama Club",
            "description": "Act, direct, and produce plays and performances",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
        },
        {
            "name": "Math Club",
            "description": "Solve challenging problems and participate in math competitions",
            "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
            "max_participants": 10,
            "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
        },
        {
            "name": "Debate Team",
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 12,
            "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
        }
    ]
    
    for activity_data in sample_activities:
        participants_emails = activity_data.pop("participants")
        activity = Activity(**activity_data)
        
        for email in participants_emails:
            participant = Participant(email=email)
            activity.participants.append(participant)
        
        db.add(activity)
    
    db.commit()



@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(db: Session = Depends(get_db)):
    """Get all activities with their details and current participant count"""
    activities = db.query(Activity).all()
    return {activity.name: activity.to_dict() for activity in activities}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Sign up a student for an activity"""
    # Find the activity
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Check if student is already signed up
    existing_participant = db.query(Participant).filter(
        Participant.activity_id == activity.id,
        Participant.email == email
    ).first()
    
    if existing_participant:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )
    
    # Check if activity is full
    if len(activity.participants) >= activity.max_participants:
        raise HTTPException(
            status_code=400,
            detail="Activity is full"
        )
    
    # Add student to activity
    try:
        participant = Participant(email=email, activity_id=activity.id)
        db.add(participant)
        db.commit()
        return {"message": f"Signed up {email} for {activity_name}"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Unregister a student from an activity"""
    # Find the activity
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Find the participant
    participant = db.query(Participant).filter(
        Participant.activity_id == activity.id,
        Participant.email == email
    ).first()
    
    if not participant:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )
    
    # Remove the participant
    db.delete(participant)
    db.commit()
    return {"message": f"Unregistered {email} from {activity_name}"}
