# generated by datamodel-codegen:
#   filename:  openapi.yaml

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, PositiveInt


class ResponseSchema(BaseModel):
    success: bool = Field(..., title='Success')
    error: str = Field(..., title='Error')


class SuccessResponseSchema(ResponseSchema):
    success: Optional[bool] = True
    error: Optional[str] = None
    data: Union[Dict[str, Any], List]


class SuccessResponseListUUID(SuccessResponseSchema):
    data: List[UUID] = Field(..., title='Data')


class ValidationError(BaseModel):
    loc: List[Union[str, int]] = Field(..., title='Location')
    msg: str = Field(..., title='Message')
    type: str = Field(..., title='Error Type')


class SGetNextTakingsResponse(BaseModel):
    schedule_id: UUID = Field(..., title='Schedule UUID')
    end_date: Optional[datetime] = Field(
        None, description='timezone is always UTC', title='End Date'
    )
    frequency: PositiveInt = Field(..., title='Frequency')
    medicine_name: str = Field(..., title='Medicine Name')
    next_taking_time: datetime = Field(..., title='Next Taking Time')
    start_date: Optional[datetime] = Field(
        None, description='timezone is always UTC', title='Start Date'
    )


class SGetScheduleResponse(BaseModel):
    schedule_id: UUID = Field(..., title='Schedule UUID')
    end_date: Optional[datetime] = Field(
        None, description='timezone is always UTC', title='End Date'
    )
    frequency: PositiveInt = Field(..., title='Frequency')
    medicine_name: str = Field(..., title='Medicine Name')
    start_date: Optional[datetime] = Field(
        None, description='timezone is always UTC', title='Start Date'
    )


class SScheduleCreateRequest(BaseModel):
    duration: Optional[timedelta] = Field(None, title='Duration')
    end_date: Optional[datetime] = Field(
        None, description='timezone is always UTC', title='End Date'
    )
    frequency: PositiveInt = Field(..., title='Frequency')
    medicine_name: str = Field(..., title='Medicine Name')
    medicine_policy: PositiveInt = Field(..., title='Medicine Policy')
    name: Optional[str] = Field(None, title='Name')
    start_date: Optional[datetime] = Field(
        None, description='timezone is always UTC', title='Start Date'
    )


class SScheduleCreateResponse(BaseModel):
    schedule_id: UUID = Field(..., title='Schedule UUID')


class SuccessResponseSGetScheduleResponse(SuccessResponseSchema):
    data: SGetScheduleResponse


class SuccessResponseSScheduleCreateResponse(SuccessResponseSchema):
    data: SScheduleCreateResponse


class SuccessResponseListSGetNextTakingsResponse(SuccessResponseSchema):
    data: List[SGetNextTakingsResponse] = Field(..., title='Data')


class HTTPValidationError(BaseModel):
    detail: Optional[List[ValidationError]] = Field(None, title='Detail')
