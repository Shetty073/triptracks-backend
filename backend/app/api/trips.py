from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any
import shutil
import os
import io
import zipfile
import aiofiles
from app.models.trip import TripDB, TripCreate, Location, Expense, EstimatedCosts, VehicleFuelCost, Leg
from app.models.user import UserDB
from app.api.auth import get_current_user, get_current_user_from_query
from app.core.database import db
from app.services.trip_planner import TripPlannerService
import uuid
from datetime import datetime
from pydantic import BaseModel
from collections import defaultdict

router = APIRouter()

def _normalize_trip(trip_data: dict) -> dict:
    """Helper to ensure legacy data matches the new TripDB schema."""
    if not trip_data:
        return trip_data
        
    if trip_data.get("status") == "in_progress":
        trip_data["status"] = "active"
        
    # Standardize photos
    if "photos" in trip_data:
        normalized_photos = []
        for photo in trip_data["photos"]:
            if isinstance(photo, str):
                normalized_photos.append({
                    "id": str(uuid.uuid4()),
                    "url": photo,
                    "uploaded_by": "",
                    "username": "legacy",
                    "album_id": "general",
                    "uploaded_at": datetime.utcnow().isoformat()
                })
            else:
                normalized_photos.append(photo)
        trip_data["photos"] = normalized_photos
    
    # Ensure mandatory lists exist
    if "albums" not in trip_data:
        trip_data["albums"] = []
    if "comments" not in trip_data:
        trip_data["comments"] = []
        
    return trip_data


# ─── SPECIFIC / LITERAL ROUTES (must come before wildcard /{trip_id}) ───────

@router.post("/", response_model=TripDB)
async def create_trip(trip: TripCreate, current_user: UserDB = Depends(get_current_user)):
    trip_db = TripDB(
        **trip.dict(),
        id=str(uuid.uuid4()),
        organizer_id=current_user.id,
        status="planned"
    )

    avg_daily = 500.0
    active_vehicles = {}
    for p in trip_db.participants:
        if p.vehicle_id:
            if p.vehicle_id not in active_vehicles:
                active_vehicles[p.vehicle_id] = {"count": 0, "mileage": 15.0, "name": "Vehicle"}
            active_vehicles[p.vehicle_id]["count"] += 1
            
    participant_uids = [p.user_id for p in trip_db.participants]
    if current_user.id not in participant_uids:
        participant_uids.append(current_user.id)
        
    users_cursor = db.db["users"].find({"id": {"$in": participant_uids}})
    all_users = await users_cursor.to_list(length=None)
    
    for u in all_users:
        vehicles = u.get("profile_settings", {}).get("vehicles", [])
        for v in vehicles:
            vid = v.get("id")
            if vid in active_vehicles:
                active_vehicles[vid]["mileage"] = v.get("mileage_per_liter", 15.0)
                active_vehicles[vid]["name"] = v.get("name") or v.get("type", "Vehicle")
                if v.get("avg_distance_per_day", 0) > avg_daily:
                    avg_daily = v.get("avg_distance_per_day")
                    
    plan = TripPlannerService.calculate_trip_itinerary(
        source=trip_db.source,
        destination=trip_db.destination,
        stops=trip_db.stops,
        avg_daily_dist=avg_daily,
    )
    
    trip_db.total_distance_km = plan["total_distance_km"]
    trip_db.total_estimated_time_mins = plan["total_estimated_time_mins"]
    trip_db.legs = plan.get("legs", [])
    days = plan.get("estimated_days", 1)
    
    total_pax = len(trip_db.participants) if trip_db.participants else 1
    est_costs = EstimatedCosts()
    
    for vid, vdata in active_vehicles.items():
        liters = trip_db.total_distance_km / (vdata["mileage"] if vdata["mileage"] > 0 else 1)
        cost = liters * trip_db.fuel_cost_per_unit
        pax_in_car = vdata["count"] or 1
        cost_per_person = cost / pax_in_car
        
        est_costs.total_fuel_cost += cost
        est_costs.vehicle_fuel_costs.append(VehicleFuelCost(
            vehicle_id=vid,
            vehicle_name=vdata["name"],
            passengers=pax_in_car,
            total_fuel_cost=round(cost, 2),
            fuel_cost_per_person=round(cost_per_person, 2)
        ))
        
    est_costs.total_fuel_cost = round(est_costs.total_fuel_cost, 2)
    
    stay_cost = current_user.profile_settings.avg_nightly_stay_expense * max(0, days - 1)
    food_cost = current_user.profile_settings.avg_daily_food_expense * days
    
    est_costs.stay_cost_per_person = round(stay_cost, 2)
    est_costs.total_stay_cost = round(stay_cost * total_pax, 2)
    
    est_costs.food_cost_per_person = round(food_cost, 2)
    est_costs.total_food_cost = round(food_cost * total_pax, 2)
    
    trip_db.estimated_costs = est_costs

    await db.db["trips"].insert_one(trip_db.dict())
    return trip_db

@router.get("/user/categories")
async def get_user_trips(current_user: UserDB = Depends(get_current_user)):
    """
    Returns trips in categories:
    - active
    - planned
    - completed
    """
    all_trips_cursor = db.db["trips"].find({
        "$or": [
            {"organizer_id": current_user.id},
            {"participants.user_id": current_user.id}
        ]
    }).sort("created_at", -1)
    
    trips = await all_trips_cursor.to_list(length=100)
    
    categorized = {
        "active": [],
        "planned": [],
        "completed": []
    }
    
    for t in trips:
        trip = TripDB(**_normalize_trip(t))
        if trip.status == "completed":
            categorized["completed"].append(trip)
        elif trip.status == "active":
            categorized["active"].append(trip)
        else:
            categorized["planned"].append(trip)
                
    return categorized

@router.get("/feed/completed", response_model=List[TripDB])
async def get_completed_trips_feed(search: Optional[str] = None, current_user: UserDB = Depends(get_current_user)):
    """Home feed showing completed public trips"""
    query: Dict[str, Any] = {"status": "completed", "is_public": True}
    
    if search:
        search_regex = {"$regex": search, "$options": "i"}
        query["$or"] = [
            {"title": search_regex},
            {"destination.name": search_regex}
        ]
        
    cursor = db.db["trips"].find(query).sort("updated_at", -1).limit(50)
    
    trips = await cursor.to_list(length=50)
    return [TripDB(**_normalize_trip(t)) for t in trips]

@router.get("/autocomplete")
async def autocomplete_location(query: str, current_user: UserDB = Depends(get_current_user)):
    return TripPlannerService.get_autocomplete(query)

class VehicleForPlan(BaseModel):
    id: str
    name: Optional[str] = None
    seats: int = 4
    mileage_per_liter: float = 15.0
    avg_distance_per_day: float = 500.0

class PlanRequest(BaseModel):
    source: Location
    destination: Location
    stops: List[Location] = []
    selected_vehicles: List[VehicleForPlan] = []  # vehicles chosen by user in UI
    fuel_price_per_liter: float = 100.0  # editable in UI

@router.post("/intelligence/plan")
async def generate_trip_plan(req: PlanRequest, current_user: UserDB = Depends(get_current_user)):
    # Use the best (max) avg_distance_per_day from chosen vehicles, then user vehicles, then fallback
    candidate_days_dists: list[float] = [v.avg_distance_per_day for v in req.selected_vehicles if v.avg_distance_per_day > 0]
    if not candidate_days_dists and current_user.profile_settings.vehicles:
        candidate_days_dists = [v.avg_distance_per_day for v in current_user.profile_settings.vehicles]
    avg_daily = max(candidate_days_dists) if candidate_days_dists else 500.0

    plan = TripPlannerService.calculate_trip_itinerary(
        source=req.source,
        destination=req.destination,
        stops=req.stops,
        avg_daily_dist=avg_daily,
    )

    total_dist = plan["total_distance_km"]
    days = plan["estimated_days"]

    # Per-vehicle fuel cost
    vehicle_fuel_costs = []
    total_fuel_cost = 0.0
    for v in req.selected_vehicles:
        liters = total_dist / v.mileage_per_liter if v.mileage_per_liter > 0 else 0
        cost = round(liters * req.fuel_price_per_liter, 2)
        total_fuel_cost += cost
        vehicle_fuel_costs.append({
            "vehicle_id": v.id,
            "vehicle_name": v.name or "Vehicle",
            "fuel_cost": cost,
            "liters_needed": round(liters, 2),
        })

    # Stay & food cost from user profile
    stay_cost = round(current_user.profile_settings.avg_nightly_stay_expense * (days - 1), 2)
    food_cost = round(current_user.profile_settings.avg_daily_food_expense * days, 2)
    total_cost = round(total_fuel_cost + stay_cost + food_cost, 2)

    plan["vehicle_fuel_costs"] = vehicle_fuel_costs
    plan["estimated_fuel_cost"] = round(total_fuel_cost, 2)
    plan["estimated_stay_cost"] = stay_cost
    plan["estimated_food_cost"] = food_cost
    plan["total_estimated_cost"] = total_cost
    plan["fuel_price_per_liter"] = req.fuel_price_per_liter

    return plan

@router.get("/{trip_id}/participants/names")
async def get_participant_names(trip_id: str, current_user: UserDB = Depends(get_current_user)):
    """Returns a map of {user_id: display_name} for all trip participants."""
    trip_data = await db.db["trips"].find_one({"id": trip_id})
    if not trip_data:
        raise HTTPException(status_code=404, detail="Trip not found")

    participant_ids = [p["user_id"] for p in trip_data.get("participants", [])]
    if trip_data.get("organizer_id") not in participant_ids:
        participant_ids.append(trip_data["organizer_id"])

    cursor = db.db["users"].find({"id": {"$in": participant_ids}})
    user_docs = await cursor.to_list(length=None)
    names = {u["id"]: u.get("full_name") or u.get("username") for u in user_docs}
    return names

class CommentCreate(BaseModel):
    text: str

@router.post("/{trip_id}/comments")
async def add_comment(trip_id: str, comment: CommentCreate, current_user: UserDB = Depends(get_current_user)):
    trip_data = await db.db["trips"].find_one({"id": trip_id})
    if not trip_data:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    # Anyone can comment on completed public trips, else only participants
    if trip_data["status"] != "completed":
        participant_ids = [p["user_id"] for p in trip_data.get("participants", [])]
        if current_user.id != trip_data["organizer_id"] and current_user.id not in participant_ids:
            raise HTTPException(status_code=403, detail="Not authorized to comment")
            
    comment_data = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.id,
        "username": current_user.username,
        "text": comment.text,
        "timestamp": datetime.utcnow()
    }
    
    await db.db["trips"].update_one(
        {"id": trip_id},
        {"$push": {"comments": comment_data}}
    )
    return comment_data

@router.post("/{trip_id}/photos")
async def add_trip_photo(
    trip_id: str, 
    file: UploadFile = File(...), 
    album_id: str = Form("general"),
    current_user: UserDB = Depends(get_current_user)
):
    trip_data = await db.db["trips"].find_one({"id": trip_id})
    if not trip_data:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    participant_ids = [p["user_id"] for p in trip_data.get("participants", [])]
    if current_user.id != trip_data["organizer_id"] and current_user.id not in participant_ids:
        raise HTTPException(status_code=403, detail="Not authorized to add photos")
        
    if trip_data.get("status") == "planned":
        raise HTTPException(status_code=400, detail="Cannot add photos to a trip that hasn't started yet")
        
    ext = file.filename.split('.')[-1] if '.' in (file.filename or "") else 'jpg'
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = f"uploads/trips/{filename}"
    
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    file_url = f"/uploads/trips/{filename}"
    
    photo_data = {
        "id": str(uuid.uuid4()),
        "url": file_url,
        "uploaded_by": current_user.id,
        "username": current_user.username,
        "album_id": album_id,
        "uploaded_at": datetime.utcnow().isoformat()
    }
    
    await db.db["trips"].update_one(
        {"id": trip_id},
        {"$push": {"photos": photo_data}}
    )
    
    return photo_data

@router.post("/{trip_id}/albums")
async def create_trip_album(
    trip_id: str, 
    name: str, 
    current_user: UserDB = Depends(get_current_user)
):
    trip_data = await db.db["trips"].find_one({"id": trip_id})
    if not trip_data:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    album_id = str(uuid.uuid4())
    album_data = {
        "id": album_id,
        "name": name,
        "created_by": current_user.id,
        "created_at": datetime.utcnow().isoformat()
    }
    
    await db.db["trips"].update_one(
        {"id": trip_id},
        {"$push": {"albums": album_data}}
    )
    
    return album_data

@router.get("/{trip_id}/albums/{album_id}/download")
async def download_trip_album(
    trip_id: str, 
    album_id: str,
    current_user: UserDB = Depends(get_current_user_from_query)
):
    trip_data = await db.db["trips"].find_one({"id": trip_id})
    if not trip_data:
        raise HTTPException(status_code=404, detail="Trip not found")

    # Authorize current user
    participant_ids = [p["user_id"] for p in trip_data.get("participants", [])]
    if current_user.id != trip_data["organizer_id"] and current_user.id not in participant_ids:
        raise HTTPException(status_code=403, detail="Not authorized to download this album")


    album_photos = [p for p in trip_data.get("photos", []) if isinstance(p, dict) and p.get("album_id") == album_id]
    
    if album_id == "general":
        legacy_photos = [p for p in trip_data.get("photos", []) if isinstance(p, str)]
        for lp in legacy_photos:
            album_photos.append({"url": lp})

    if not album_photos:
        raise HTTPException(status_code=404, detail="No photos found in this album")

    async def zip_generator():
        io_output = io.BytesIO()
        with zipfile.ZipFile(io_output, mode='w', compression=zipfile.ZIP_DEFLATED) as zip_file:
            for photo in album_photos:
                url = photo.get("url")
                relative_path = url.lstrip("/")
                if os.path.exists(relative_path):
                    filename = os.path.basename(relative_path)
                    async with aiofiles.open(relative_path, mode='rb') as f:
                        content = await f.read()
                        zip_file.writestr(filename, content)
        
        yield io_output.getvalue()

    album_name = next((a["name"] for a in trip_data.get("albums", []) if a["id"] == album_id), "album")
    if album_id == "general":
        album_name = "General"

    return StreamingResponse(
        zip_generator(),
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename={album_name}.zip"}
    )

# ─── WILDCARD ROUTES (must come AFTER all literal routes) ────────────────────

@router.get("/{trip_id}", response_model=TripDB)
async def get_trip(trip_id: str, current_user: UserDB = Depends(get_current_user)):
    trip_data = await db.db["trips"].find_one({"id": trip_id})
    if not trip_data:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    # Only participants can view, unless it's a completed public trip
    is_completed_public = trip_data.get("status") == "completed" and trip_data.get("is_public", False)
    if not is_completed_public:
        participant_ids = [p["user_id"] for p in trip_data.get("participants", [])]
        if current_user.id != trip_data["organizer_id"] and current_user.id not in participant_ids:
            raise HTTPException(status_code=403, detail="Not authorized to view this trip")
            
    # Normalize photos: convert legacy string URLs to TripPhoto objects
    if "photos" in trip_data:
        normalized_photos = []
        for photo in trip_data["photos"]:
            if isinstance(photo, str):
                normalized_photos.append({
                    "id": str(uuid.uuid4()),
                    "url": photo,
                    "uploaded_by": "",
                    "username": "legacy",
                    "album_id": "general",
                    "uploaded_at": datetime.utcnow().isoformat()
                })
            else:
                normalized_photos.append(photo)
        trip_data["photos"] = normalized_photos

    if "photos" in trip_data:
        _normalize_trip(trip_data)

    return TripDB(**trip_data)

@router.patch("/{trip_id}/start", response_model=TripDB)
async def start_trip(trip_id: str, force: bool = False, current_user: UserDB = Depends(get_current_user)):
    trip_data = await db.db["trips"].find_one({"id": trip_id})
    if not trip_data:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip_data["organizer_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Only the organizer can start the trip")
        
    if trip_data["status"] != "planned":
        raise HTTPException(status_code=400, detail=f"Trip cannot be started from status: {trip_data['status']}")

    all_users = [p["user_id"] for p in trip_data.get("participants", [])]
    if current_user.id not in all_users:
        all_users.append(current_user.id)

    active_trips_cursor = db.db["trips"].find({
        "status": {"$in": ["in_progress", "active"]},
        "$or": [
            {"organizer_id": {"$in": all_users}},
            {"participants.user_id": {"$in": all_users}}
        ]
    })
    
    active_trips = await active_trips_cursor.to_list(length=None)
    
    conflicting_user_ids = set()
    for active_trip in active_trips:
        if active_trip["organizer_id"] in all_users:
            conflicting_user_ids.add(active_trip["organizer_id"])
        for p in active_trip.get("participants", []):
            if p["user_id"] in all_users:
                conflicting_user_ids.add(p["user_id"])
                
    if conflicting_user_ids:
        if force:
            new_participants = [p for p in trip_data.get("participants", []) if p["user_id"] not in conflicting_user_ids]
            await db.db["trips"].update_one(
                {"id": trip_id},
                {"$set": {"participants": new_participants}}
            )
        else:
            users_cursor = db.db["users"].find({"id": {"$in": list(conflicting_user_ids)}})
            bad_users = await users_cursor.to_list(length=None)
            names = [u.get("full_name") or u.get("username") for u in bad_users]
            names_str = ", ".join(names)
            raise HTTPException(
                status_code=400, 
                detail=f"Unable to start trip as the following users already have an active trip: {names_str}. Use force=true to remove them and start anyway."
            )
            
    await db.db["trips"].update_one(
        {"id": trip_id},
        {"$set": {"status": "active", "start_date": datetime.utcnow(), "updated_at": datetime.utcnow()}}
    )
    
    updated_trip = await db.db["trips"].find_one({"id": trip_id})
    # Normalize photos
    if "photos" in updated_trip:
        normalized_photos = []
        for photo in updated_trip["photos"]:
            if isinstance(photo, str):
                normalized_photos.append({
                    "id": str(uuid.uuid4()),
                    "url": photo,
                    "uploaded_by": "",
                    "username": "legacy",
                    "album_id": "general",
                    "uploaded_at": datetime.utcnow().isoformat()
                })
            else:
                normalized_photos.append(photo)
        updated_trip["photos"] = normalized_photos
        
    return TripDB(**updated_trip)

class CompleteTripRequest(BaseModel):
    road_condition: Optional[str] = None
    description: Optional[str] = None
    is_public: bool = False

@router.patch("/{trip_id}/complete", response_model=TripDB)
async def complete_trip(trip_id: str, payload: CompleteTripRequest, current_user: UserDB = Depends(get_current_user)):
    trip_data = await db.db["trips"].find_one({"id": trip_id})
    if not trip_data:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    if trip_data["organizer_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Only the organizer can complete the trip")
        
    await db.db["trips"].update_one(
        {"id": trip_id},
        {"$set": {
            "status": "completed", 
            "end_date": datetime.utcnow(), 
            "updated_at": datetime.utcnow(),
            "road_condition": payload.road_condition,
            "description": payload.description,
            "is_public": payload.is_public
        }}
    )
    
    updated_trip = await db.db["trips"].find_one({"id": trip_id})
    return TripDB(**_normalize_trip(updated_trip))

@router.post("/{trip_id}/expenses", response_model=Expense)
async def add_expense(trip_id: str, expense: Expense, current_user: UserDB = Depends(get_current_user)):
    trip_data = await db.db["trips"].find_one({"id": trip_id})
    if not trip_data:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    participant_ids = [p["user_id"] for p in trip_data.get("participants", [])]
    if current_user.id != trip_data["organizer_id"] and current_user.id not in participant_ids:
        raise HTTPException(status_code=403, detail="Not authorized to add expenses")
        
    expense.id = str(uuid.uuid4())
    if not expense.paid_by:
        expense.paid_by = current_user.id
        
    await db.db["trips"].update_one(
        {"id": trip_id},
        {"$push": {"expenses": expense.dict()}}
    )
    return expense

@router.get("/{trip_id}/balances")
async def get_trip_balances(trip_id: str, current_user: UserDB = Depends(get_current_user)):
    trip_data = await db.db["trips"].find_one({"id": trip_id})
    if not trip_data:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    balances = defaultdict(float)
    
    participants = [p["user_id"] for p in trip_data.get("participants", [])]
    if trip_data.get("organizer_id") not in participants:
        participants.append(trip_data.get("organizer_id"))
        
    for expense in trip_data.get("expenses", []):
        amount = expense.get("amount", 0.0)
        paid_by = expense.get("paid_by")
        
        balances[paid_by] += amount
        
        splits = expense.get("splits", {})
        if splits:
            for debtor_id, owed_amount in splits.items():
                balances[debtor_id] -= owed_amount
        elif participants:
            split_amount = amount / len(participants)
            for uid in participants:
                balances[uid] -= split_amount

    # Always fetch names for ALL participants, even if they have no expenses yet
    users_cursor = db.db["users"].find({"id": {"$in": participants}})
    user_docs = await users_cursor.to_list(length=None)
    user_names = {u["id"]: u.get("full_name") or u.get("username") for u in user_docs}
    
    debtors = []
    creditors = []
    
    for uid, net in balances.items():
        if round(net, 2) < 0:
            debtors.append({"user_id": uid, "name": user_names.get(uid, "Unknown"), "amount": abs(round(net, 2))})
        elif round(net, 2) > 0:
            creditors.append({"user_id": uid, "name": user_names.get(uid, "Unknown"), "amount": round(net, 2)})

    debtors.sort(key=lambda x: x["amount"], reverse=True)
    creditors.sort(key=lambda x: x["amount"], reverse=True)
    
    transfers = []
    i = 0
    j = 0
    while i < len(debtors) and j < len(creditors):
        debtor = debtors[i]
        creditor = creditors[j]
        
        min_amount = min(debtor["amount"], creditor["amount"])
        if min_amount > 0:
            transfers.append({
                "from_user_id": debtor["user_id"],
                "from_name": debtor["name"],
                "to_user_id": creditor["user_id"],
                "to_name": creditor["name"],
                "amount": round(min_amount, 2)
            })
            
        debtor["amount"] -= min_amount
        creditor["amount"] -= min_amount
        
        if round(debtor["amount"], 2) == 0:
            i += 1
        if round(creditor["amount"], 2) == 0:
            j += 1
            
    return {
        "balances": {uid: round(bal, 2) for uid, bal in balances.items()}, 
        "transfers": transfers,
        "user_names": user_names
    }



