from pydantic import BaseModel
from datetime import datetime, timedelta


class UserTest(BaseModel):
    name: str
    medicine_policy: int


class MedicineTest(BaseModel):
    medicine_name: str
    frequency: int
    start_date: datetime
    end_date: datetime
    duration: timedelta
