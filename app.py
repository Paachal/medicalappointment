from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Optional

app = FastAPI()

# In-memory database
patients_db: Dict[int, dict] = {}
doctors_db: Dict[int, dict] = {}
appointments_db: List[dict] = []

class Patient(BaseModel):
    name: str
    age: int
    sex: str
    weight: float
    height: float
    phone: str

class Doctor(BaseModel):
    name: str
    specialization: str
    phone: str
    is_available: Optional[bool] = True

class Appointment(BaseModel):
    patient_id: int
    doctor_id: int
    date: datetime

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the medical appointment API!"}

# CRUD endpoints for Patients
@app.get("/patients", response_model=List[Patient])
async def get_patients():
    return list(patients_db.values())

@app.get("/patients/{patient_id}", response_model=Patient)
async def get_patient(patient_id: int):
    return patients_db.get(patient_id)

@app.post("/patients", response_model=dict)
async def create_patient(patient: Patient):
    patient_id = len(patients_db) + 1
    patients_db[patient_id] = patient.dict()
    return {"message": "Patient created successfully", "patient_id": patient_id}

@app.put("/patients/{patient_id}", response_model=dict)
async def update_patient(patient_id: int, patient: Patient):
    patients_db[patient_id].update(patient.dict())
    return {"message": "Patient updated successfully"}

@app.delete("/patients/{patient_id}", response_model=dict)
async def delete_patient(patient_id: int):
    del patients_db[patient_id]
    return {"message": "Patient deleted successfully"}

# CRUD endpoints for Doctors
@app.get("/doctors", response_model=List[Doctor])
async def get_doctors():
    return list(doctors_db.values())

@app.get("/doctors/{doctor_id}", response_model=Doctor)
async def get_doctor(doctor_id: int):
    return doctors_db.get(doctor_id)

@app.post("/doctors", response_model=dict)
async def create_doctor(doctor: Doctor):
    doctor_id = len(doctors_db) + 1
    doctors_db[doctor_id] = doctor.dict()
    return {"message": "Doctor created successfully", "doctor_id": doctor_id}

@app.put("/doctors/{doctor_id}", response_model=dict)
async def update_doctor(doctor_id: int, doctor: Doctor):
    doctors_db[doctor_id].update(doctor.dict())
    return {"message": "Doctor updated successfully"}

@app.delete("/doctors/{doctor_id}", response_model=dict)
async def delete_doctor(doctor_id: int):
    del doctors_db[doctor_id]
    return {"message": "Doctor deleted successfully"}

# Create an appointment
@app.post("/appointments", response_model=dict)
async def create_appointment(patient_id: int):
    available_doctors = [doc_id for doc_id, doc in doctors_db.items() if doc["is_available"]]
    if not available_doctors:
        raise HTTPException(status_code=400, detail="No available doctors at the moment")
    doctor_id = available_doctors[0]
    appointment = Appointment(patient_id=patient_id, doctor_id=doctor_id, date=datetime.now())
    appointments_db.append(appointment.dict())
    doctors_db[doctor_id]["is_available"] = False
    return {"message": "Appointment created successfully"}

# Complete an appointment
@app.put("/appointments/{appointment_id}/complete", response_model=dict)
async def complete_appointment(appointment_id: int):
    appointment = next((app for app in appointments_db if app["id"] == appointment_id), None)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    doctor_id = appointment["doctor_id"]
    doctors_db[doctor_id]["is_available"] = True
    appointments_db.remove(appointment)
    return {"message": "Appointment completed successfully"}

# Cancel an appointment
@app.delete("/appointments/{appointment_id}", response_model=dict)
async def cancel_appointment(appointment_id: int):
    appointment = next((app for app in appointments_db if app["id"] == appointment_id), None)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    doctor_id = appointment["doctor_id"]
    doctors_db[doctor_id]["is_available"] = True
    appointments_db.remove(appointment)
    return {"message": "Appointment canceled successfully"}

# Set availability status for Doctors
@app.put("/doctors/{doctor_id}/availability", response_model=dict)
async def set_doctor_availability(doctor_id: int, is_available: bool):
    doctors_db[doctor_id]["is_available"] = is_available
    return {"message": "Doctor availability status updated successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
