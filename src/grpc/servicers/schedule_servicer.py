from contextlib import asynccontextmanager
from typing import AsyncGenerator

from src.database.connection import AsyncSessionMaker

from src.api.v1.schedule.service import ScheduleService
from src.api.v1.schedule.schemas import SScheduleCreateRequest
from src.grpc.schedule_pb2 import (
    CreateScheduleRequest,
    CreateScheduleResponse,
    GetScheduleRequest,
    GetScheduleResponse,
    GetSchedulesIdsRequest,
    GetSchedulesIdsResponse,
    GetNextTakingsRequest,
    GetNextTakingsResponse,
    ScheduleInfo,
    NextTakingInfo,
)

from src.grpc.servicers.utils import (
    convert_from_timestamp,
    convert_from_duration,
    convert_to_timestamp,
)


class ScheduleServicer:
    def __init__(self, schedule_service: ScheduleService | None = None):
        self.service: ScheduleService | None = schedule_service
        if self.service is None:
            self.service: ScheduleService = ScheduleService(AsyncSessionMaker())

    async def CreateSchedule(self, request: CreateScheduleRequest, context):
        schedule_create_dto = SScheduleCreateRequest(
            name=request.name,
            medicine_policy=request.medicine_policy,
            medicine_name=request.medicine_name,
            frequency=request.frequency,
            start_date=convert_from_timestamp(request, "start_date"),
            end_date=convert_from_timestamp(request, "end_date"),
            duration=convert_from_duration(request, "duration"),
        )
        response = await self.service.create_schedule(schedule_create_dto)
        return CreateScheduleResponse(id=str(response))

    async def GetSchedule(self, request: GetScheduleRequest, context):
        response = await self.service.get_schedule_by_id(request.user_id, request.schedule_id)
        return GetScheduleResponse(
            schedule=ScheduleInfo(
                medicine_name=response.medicine_name,
                frequency=response.frequency,
                start_date=convert_to_timestamp(response.start_date),
                end_date=convert_to_timestamp(response.end_date),
            )
        )

    async def GetSchedulesIds(self, request: GetSchedulesIdsRequest, context):
        response = await self.service.get_schedules_ids_by_policy(request.user_id)
        return GetSchedulesIdsResponse(schedule_ids=[str(schedule_id) for schedule_id in response])

    async def GetNextTakings(self, request: GetNextTakingsRequest, context):
        response = await self.service.get_next_takings(
            request.user_id, request.next_takings_interval
        )
        takings = []
        for taking in response:
            schedule_info = ScheduleInfo(
                medicine_name=taking["schedule"].medicine_name,
                frequency=taking["schedule"].frequency,
                start_date=convert_to_timestamp(taking["schedule"].start_date),
                end_date=convert_to_timestamp(taking["schedule"].end_date),
            )

            taking_info = NextTakingInfo(
                schedule_info=schedule_info,
                next_taking_time=convert_to_timestamp(taking["next_taking_time"]),
            )

            takings.append(taking_info)

        return GetNextTakingsResponse(takings=takings)
