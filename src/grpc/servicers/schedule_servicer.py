from contextlib import asynccontextmanager

from src.api.v1.schedule.schemas import SScheduleCreateRequest
from src.api.v1.schedule.service import ScheduleService
from src.database.connection import AsyncSessionMaker
from src.grpc.schedule_pb2 import (
    CreateScheduleRequest,
    CreateScheduleResponse,
    GetNextTakingsRequest,
    GetNextTakingsResponse,
    GetScheduleRequest,
    GetScheduleResponse,
    GetSchedulesIdsRequest,
    GetSchedulesIdsResponse,
    NextTakingInfo,
    ScheduleInfo,
)
from src.grpc.schedule_pb2_grpc import ScheduleServiceServicer
from src.grpc.servicers.utils import (
    convert_from_duration,
    convert_from_timestamp,
    convert_to_timestamp,
)
from src.repositories import ScheduleRepository, UserRepository


class ScheduleServicer(ScheduleServiceServicer):
    def __init__(self, schedule_service: ScheduleService | None = None):
        super().__init__()
        self.service: ScheduleService | None = schedule_service

    @asynccontextmanager
    async def get_service(self):
        if self.service is None:
            async with AsyncSessionMaker() as session:
                user_repo: UserRepository = UserRepository(session)
                schedule_repo: ScheduleRepository = ScheduleRepository(session)
                yield ScheduleService(
                    user_repo=user_repo, schedule_repo=schedule_repo
                )

    async def CreateSchedule(self, request: CreateScheduleRequest, context):
        async with self.get_service() as service:
            schedule_create_dto = SScheduleCreateRequest(
                name=request.name,
                medicine_policy=request.medicine_policy,
                medicine_name=request.medicine_name,
                frequency=request.frequency,
                start_date=convert_from_timestamp(request, "start_date"),
                end_date=convert_from_timestamp(request, "end_date"),
                duration=convert_from_duration(request, "duration"),
            )
            response = await service.create_schedule(schedule_create_dto)
        return CreateScheduleResponse(id=str(response))

    async def GetSchedule(self, request: GetScheduleRequest, context):
        async with self.get_service() as service:
            response = await service.get_schedule_by_id(request.user_id, request.schedule_id)
        return GetScheduleResponse(
            schedule=ScheduleInfo(
                medicine_name=response.medicine_name,
                frequency=response.frequency,
                start_date=convert_to_timestamp(response.start_date),
                end_date=convert_to_timestamp(response.end_date),
            )
        )

    async def GetSchedulesIds(self, request: GetSchedulesIdsRequest, context):
        async with self.get_service() as service:
            response = await service.get_schedules_ids_by_policy(request.user_id)
        return GetSchedulesIdsResponse(schedule_ids=[str(schedule_id) for schedule_id in response])

    async def GetNextTakings(self, request: GetNextTakingsRequest, context):
        async with self.get_service() as service:
            response = await service.get_next_takings(
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
