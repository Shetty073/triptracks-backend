from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
import uuid

class Location(BaseModel):
    name: str # The autocomplete name
    lat: float
    lng: float

class Leg(BaseModel):
    distance_km: float
    estimated_time_mins: int

class TripParticipant(BaseModel):
    user_id: str
    is_driver: bool = False
    vehicle_id: Optional[str] = None # Which vehicle they are in
    role: str = "passenger" # e.g. "driver", "passenger", "organizer"

class Expense(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    category: str = "Miscellaneous"
    amount: float
    paid_by: str # user_id
    splits: Dict[str, float] = {} # user_id -> explicit amount owed
    date: datetime = Field(default_factory=datetime.utcnow)

class VehicleFuelCost(BaseModel):
    vehicle_id: str
    vehicle_name: str
    passengers: int
    total_fuel_cost: float
    fuel_cost_per_person: float

class EstimatedCosts(BaseModel):
    vehicle_fuel_costs: List[VehicleFuelCost] = []
    total_fuel_cost: float = 0.0
    total_stay_cost: float = 0.0
    stay_cost_per_person: float = 0.0
    total_food_cost: float = 0.0
    food_cost_per_person: float = 0.0

class TripBase(BaseModel):
    title: str
    source: Location
    destination: Location
    stops: List[Location] = []
    participants: List[TripParticipant] = []
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    fuel_cost_per_unit: float = 0.0
    legs: List[Leg] = []
    total_distance_km: float = 0.0
    total_estimated_time_mins: int = 0

class TripCreate(TripBase):
    pass

class TripComment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    username: str
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TripPhoto(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: str
    uploaded_by: str
    username: str
    album_id: Optional[str] = "general"
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class TripAlbum(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TripDB(TripBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organizer_id: str
    status: str = "planned" # planned, active, completed
    expenses: List[Expense] = []
    comments: List[TripComment] = []
    photos: List[TripPhoto] = []
    albums: List[TripAlbum] = []
    estimated_costs: Optional[EstimatedCosts] = None
    road_condition: Optional[str] = None
    description: Optional[str] = None
    is_public: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
