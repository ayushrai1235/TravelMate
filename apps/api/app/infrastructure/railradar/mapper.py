"""Mapper: RailRadar external schemas -> internal domain models."""
from __future__ import annotations

from app.infrastructure.railradar.schemas import (
    RailRadarJourney,
    RailRadarTrain,
    RailRadarStatusResponse,
    RailRadarRouteResponse,
    RailRadarStationBoardResponse,
    RailRadarTrainDetailsResponse,
    RailRadarStation,
    RailRadarScheduleStop,
    RailRadarStationSearchResponse,
    RailRadarRouteStop,
    RailRadarStationInfo,
    RailRadarTrainLookupResponse,
    RailRadarStationLookupResponse,
)
from app.domain.models.railradar import (
    Station,
    Train,
    Journey,
    RunningStatus,
    RouteGeometry,
    StationBoardEntry,
    TrainDetails,
    StationLookupResult,
    StationSearchResponse,
    StationSchedule,
    RouteStop,
    CurrentLocation,
    HaltInfo,
    ExceptionInfo,
)


class RailRadarMapper:
    """Static mapper from RailRadar schemas to domain models."""

    @staticmethod
    def _is_dict(obj):
        return isinstance(obj, dict)

    @staticmethod
    def _to_station(rk) -> Station:
        if RailRadarMapper._is_dict(rk):
            return Station(
                code=rk.get("code", ""),
                name=rk.get("name", ""),
                zone=rk.get("zone"),
                state=rk.get("state"),
                latitude=rk.get("latitude"),
                longitude=rk.get("longitude"),
            )
        return Station(
            code=rk.code,
            name=rk.name,
            zone=rk.zone,
            state=rk.state,
            latitude=rk.latitude,
            longitude=rk.longitude,
        )

    @staticmethod
    def _to_station_info(rk) -> Station:
        if RailRadarMapper._is_dict(rk):
            return Station(code=rk.get("code", ""), name=rk.get("name", ""))
        return Station(
            code=rk.code,
            name=rk.name,
        )

    @staticmethod
    def _to_schedule_stop(rk) -> StationSchedule:
        if RailRadarMapper._is_dict(rk):
            station = rk.get("station")
            if RailRadarMapper._is_dict(station):
                station_code = station.get("code", "")
                station_name = station.get("name", "")
            else:
                station_code = rk.get("station_code", "") or ""
                station_name = rk.get("station_name", "") or ""
            return StationSchedule(
                station_code=station_code,
                station_name=station_name,
                arrival=rk.get("arrival") or rk.get("arrival_time"),
                departure=rk.get("departure") or rk.get("departure_time"),
                halt=rk.get("halt") or rk.get("halt_minutes", 0),
                distance=rk.get("distance") or rk.get("distance_km", 0.0),
                day=rk.get("day") or rk.get("day_count") or rk.get("arrivalDay") or 1,
                platform=rk.get("platform"),
                sequence=rk.get("sequence"),
                arrival_day=rk.get("arrivalDay"),
                departure_day=rk.get("departureDay"),
            )

        if rk.station:
            station_code = rk.station.code
            station_name = rk.station.name
        else:
            station_code = rk.station_code or ""
            station_name = rk.station_name or ""
        return StationSchedule(
            station_code=station_code,
            station_name=station_name,
            arrival=rk.arrival or rk.arrival_time,
            departure=rk.departure or rk.departure_time,
            halt=rk.halt or rk.halt_minutes,
            distance=rk.distance or rk.distance_km,
            day=rk.day or rk.day_count or rk.arrivalDay or 1,
            platform=rk.platform,
            sequence=rk.sequence,
            arrival_day=rk.arrivalDay,
            departure_day=rk.departureDay,
        )

    @staticmethod
    def _to_route_stop(rk) -> RouteStop:
        if RailRadarMapper._is_dict(rk):
            station = rk.get("station")
            if RailRadarMapper._is_dict(station):
                station_code = station.get("code", "")
                station_name = station.get("name", "")
            else:
                station_code = rk.get("station_code", "") or ""
                station_name = rk.get("station_name", "") or ""
            return RouteStop(
                station_code=station_code,
                station_name=station_name,
                arrival=rk.get("arrival") or rk.get("arrival_time"),
                departure=rk.get("departure") or rk.get("departure_time"),
                halt_minutes=rk.get("halt") or rk.get("halt_minutes", 0),
                distance_km=rk.get("distance") or rk.get("distance_km", 0.0),
                day=rk.get("day") or rk.get("day_count") or rk.get("arrivalDay") or 1,
                platform=rk.get("platform"),
                latitude=rk.get("lat"),
                longitude=rk.get("lng"),
                is_halt=rk.get("isHalt"),
                speed_to_next_station_kmph=rk.get("speedToNextStationKmph"),
            )

        if rk.station:
            station_code = rk.station.code
            station_name = rk.station.name
        else:
            station_code = rk.station_code or ""
            station_name = rk.station_name or ""
        return RouteStop(
            station_code=station_code,
            station_name=station_name,
            arrival=rk.arrival or rk.arrival_time,
            departure=rk.departure or rk.departure_time,
            halt_minutes=rk.halt or rk.halt_minutes,
            distance_km=rk.distance or rk.distance_km,
            day=rk.day or rk.day_count or rk.arrivalDay or 1,
            platform=rk.platform,
            latitude=rk.lat,
            longitude=rk.lng,
            is_halt=rk.isHalt,
            speed_to_next_station_kmph=rk.speedToNextStationKmph,
        )

    @staticmethod
    def _to_route_stop_from_route(rk) -> RouteStop:
        if RailRadarMapper._is_dict(rk):
            return RouteStop(
                station_code=rk.get("code", ""),
                station_name=rk.get("name", ""),
                latitude=rk.get("lat"),
                longitude=rk.get("lng"),
                sequence=rk.get("sequence"),
            )
        return RouteStop(
            station_code=rk.code or "",
            station_name=rk.name or "",
            latitude=rk.lat,
            longitude=rk.lng,
            sequence=rk.sequence,
        )

    @staticmethod
    def _to_journey_dict(rk: dict) -> Journey:
        source = rk.get("source")
        if RailRadarMapper._is_dict(source):
            source = RailRadarStation(code=source.get("code", ""), name=source.get("name", ""))
        dest = rk.get("destination")
        if RailRadarMapper._is_dict(dest):
            dest = RailRadarStation(code=dest.get("code", ""), name=dest.get("name", ""))
        return Journey(
            train_number=rk.get("train_number", ""),
            train_name=rk.get("train_name", ""),
            train_type=rk.get("train_type", ""),
            source=RailRadarMapper._to_station(source),
            destination=RailRadarMapper._to_station(dest),
            departure_time=rk.get("departure_time", ""),
            arrival_time=rk.get("arrival_time", ""),
            duration_minutes=rk.get("duration_minutes", 0),
            distance_km=rk.get("distance_km", 0.0),
            runs_days=rk.get("runs_days", []),
            classes=rk.get("classes", []),
            classes_available=rk.get("classes_available", []),
            train_code=rk.get("train_code"),
            live=rk.get("live"),
        )

    @staticmethod
    def _to_train_dict(rk: dict) -> Train:
        source = RailRadarMapper._to_station_info(rk.get("source", {}))
        dest = RailRadarMapper._to_station_info(rk.get("destination", {}))
        run_days = rk.get("runDays") or rk.get("runs_days", [])
        return Train(
            number=rk.get("number", ""),
            name=rk.get("name", ""),
            train_type=rk.get("type", ""),
            category=rk.get("category"),
            source_station=source,
            destination_station=dest,
            run_days=run_days,
            runs_days=run_days,
            distance_km=rk.get("distance_km") or rk.get("distance"),
            duration_minutes=rk.get("duration_minutes") or rk.get("duration"),
            avg_speed=rk.get("avgSpeed") or rk.get("avg_speed"),
            max_speed=rk.get("maxSpeed") or rk.get("max_speed"),
            total_halts=rk.get("totalHalts") or rk.get("total_halts"),
            return_train=rk.get("returnTrain"),
            coach_position=rk.get("coachPosition"),
        )

    @staticmethod
    def map_journey(rk) -> Journey:
        if RailRadarMapper._is_dict(rk):
            return RailRadarMapper._to_journey_dict(rk)
        source = rk.source
        if isinstance(source, RailRadarStationInfo):
            source = RailRadarStation(code=source.code, name=source.name)
        dest = rk.destination
        if isinstance(dest, RailRadarStationInfo):
            dest = RailRadarStation(code=dest.code, name=dest.name)
        return Journey(
            train_number=rk.train_number,
            train_name=rk.train_name,
            train_type=rk.train_type,
            source=RailRadarMapper._to_station(source),
            destination=RailRadarMapper._to_station(dest),
            departure_time=rk.departure_time or "",
            arrival_time=rk.arrival_time or "",
            duration_minutes=rk.duration_minutes or 0,
            distance_km=rk.distance_km or 0.0,
            runs_days=rk.runs_days,
            classes=rk.classes,
            classes_available=rk.classes_available,
            train_code=rk.train_code,
            live=rk.live,
        )

    @staticmethod
    def map_train(rk) -> Train:
        if RailRadarMapper._is_dict(rk):
            return RailRadarMapper._to_train_dict(rk)
        source = RailRadarMapper._to_station_info(rk.source)
        dest = RailRadarMapper._to_station_info(rk.destination)
        run_days = rk.runDays or rk.runs_days
        return Train(
            number=rk.number,
            name=rk.name,
            train_type=rk.type,
            category=rk.category,
            source_station=source,
            destination_station=dest,
            run_days=run_days,
            runs_days=run_days,
            distance_km=rk.distance_km or rk.distance,
            duration_minutes=rk.duration_minutes or rk.duration,
            avg_speed=rk.avgSpeed or rk.avg_speed,
            max_speed=rk.maxSpeed or rk.max_speed,
            total_halts=rk.totalHalts or rk.total_halts,
            return_train=rk.returnTrain,
            coach_position=rk.coachPosition,
        )

    @staticmethod
    def map_running_status(rk) -> RunningStatus:
        if RailRadarMapper._is_dict(rk):
            current_loc = rk.get("currentLocation") or rk.get("current_location")
            current_station_code = None
            current_station_name = None
            if current_loc and RailRadarMapper._is_dict(current_loc):
                current_station_code = current_loc.get("stationCode") or current_loc.get("current_station_code")
                current_station_name = current_loc.get("current_station_name")
            elif rk.get("current_station_code"):
                current_station_code = rk.get("current_station_code")
                current_station_name = rk.get("current_station_name")
            delay = rk.get("delayMinutes") if rk.get("delayMinutes") is not None else rk.get("delay_minutes", 0)
            train_data = rk.get("train")
            train_obj = RailRadarMapper.map_train(train_data) if train_data else None
            prev_halt = rk.get("previousHalt") or rk.get("previous_halt")
            next_halt = rk.get("nextHalt") or rk.get("next_halt")
            exceptions = []
            for e in (rk.get("exceptions") or []):
                if RailRadarMapper._is_dict(e):
                    exceptions.append(ExceptionInfo(
                        type=e.get("type"),
                        message=e.get("message"),
                        diverted=e.get("diverted"),
                        partially_cancelled=e.get("partiallyCancelled"),
                        rescheduled=e.get("rescheduled"),
                    ))
            route = [RailRadarMapper._to_schedule_stop(s) for s in (rk.get("route") or [])]
            return RunningStatus(
                train_number=rk.get("trainNumber") or rk.get("train_number", ""),
                train_name=rk.get("trainName") or rk.get("train_name"),
                current_station_code=current_station_code,
                current_station_name=current_station_name,
                status=rk.get("status") or "unknown",
                delay_minutes=delay or 0,
                last_updated=rk.get("lastUpdatedAt") or rk.get("last_updated"),
                reported_at=rk.get("reported_at"),
                start_date=rk.get("startDate"),
                train=train_obj,
                current_location=CurrentLocation(
                    station_code=current_loc.get("stationCode") if current_loc and RailRadarMapper._is_dict(current_loc) else None,
                    sequence=current_loc.get("sequence") if current_loc and RailRadarMapper._is_dict(current_loc) else None,
                    status=current_loc.get("status") if current_loc and RailRadarMapper._is_dict(current_loc) else None,
                    is_halt=current_loc.get("isHalt") if current_loc and RailRadarMapper._is_dict(current_loc) else None,
                    is_diverted=current_loc.get("isDiverted") if current_loc and RailRadarMapper._is_dict(current_loc) else None,
                    is_actual_position=current_loc.get("isActualPosition") if current_loc and RailRadarMapper._is_dict(current_loc) else None,
                    segment_progress=current_loc.get("segmentProgress") if current_loc and RailRadarMapper._is_dict(current_loc) else None,
                    speed_kmh=current_loc.get("speedKmh") if current_loc and RailRadarMapper._is_dict(current_loc) else None,
                    bearing_degrees=current_loc.get("bearingDegrees") if current_loc and RailRadarMapper._is_dict(current_loc) else None,
                ) if current_loc and RailRadarMapper._is_dict(current_loc) else None,
                previous_halt=HaltInfo(
                    station_code=prev_halt.get("stationCode") if prev_halt and RailRadarMapper._is_dict(prev_halt) else None,
                    station_name=prev_halt.get("station_name") if prev_halt and RailRadarMapper._is_dict(prev_halt) else None,
                    sequence=prev_halt.get("sequence") if prev_halt and RailRadarMapper._is_dict(prev_halt) else None,
                    distance=prev_halt.get("distance") if prev_halt and RailRadarMapper._is_dict(prev_halt) else None,
                ) if prev_halt and RailRadarMapper._is_dict(prev_halt) else None,
                next_halt=HaltInfo(
                    station_code=next_halt.get("stationCode") if next_halt and RailRadarMapper._is_dict(next_halt) else None,
                    station_name=next_halt.get("station_name") if next_halt and RailRadarMapper._is_dict(next_halt) else None,
                    sequence=next_halt.get("sequence") if next_halt and RailRadarMapper._is_dict(next_halt) else None,
                    distance=next_halt.get("distance") if next_halt and RailRadarMapper._is_dict(next_halt) else None,
                ) if next_halt and RailRadarMapper._is_dict(next_halt) else None,
                exceptions=exceptions,
                route=route,
                is_live=rk.get("isLive"),
            )

        train_number = rk.trainNumber or rk.train_number or ""
        train_name = rk.trainName or rk.train_name
        current_loc = rk.currentLocation or rk.current_location
        current_station_code = None
        current_station_name = None
        if current_loc:
            current_station_code = current_loc.stationCode or current_loc.current_station_code
            current_station_name = current_loc.current_station_name
        elif rk.current_station_code:
            current_station_code = rk.current_station_code
            current_station_name = rk.current_station_name
        delay = rk.delayMinutes if rk.delayMinutes is not None else rk.delay_minutes
        return RunningStatus(
            train_number=train_number,
            train_name=train_name,
            current_station_code=current_station_code,
            current_station_name=current_station_name,
            status=rk.status or "unknown",
            delay_minutes=delay or 0,
            last_updated=rk.lastUpdatedAt or rk.last_updated,
            reported_at=rk.reported_at,
            start_date=rk.startDate,
            train=RailRadarMapper.map_train(rk.train) if rk.train else None,
            current_location=CurrentLocation(
                station_code=current_loc.stationCode if current_loc else None,
                sequence=current_loc.sequence if current_loc else None,
                status=current_loc.status if current_loc else None,
                is_halt=current_loc.isHalt if current_loc else None,
                is_diverted=current_loc.isDiverted if current_loc else None,
                is_actual_position=current_loc.isActualPosition if current_loc else None,
                segment_progress=current_loc.segmentProgress if current_loc else None,
                speed_kmh=current_loc.speedKmh if current_loc else None,
                bearing_degrees=current_loc.bearingDegrees if current_loc else None,
            ) if current_loc else None,
            previous_halt=HaltInfo(
                station_code=rk.previousHalt.stationCode if rk.previousHalt else None,
                station_name=rk.previousHalt.station_name if rk.previousHalt else None,
                sequence=rk.previousHalt.sequence if rk.previousHalt else None,
                distance=rk.previousHalt.distance if rk.previousHalt else None,
            ) if rk.previousHalt else None,
            next_halt=HaltInfo(
                station_code=rk.nextHalt.stationCode if rk.nextHalt else None,
                station_name=rk.nextHalt.station_name if rk.nextHalt else None,
                sequence=rk.nextHalt.sequence if rk.nextHalt else None,
                distance=rk.nextHalt.distance if rk.nextHalt else None,
            ) if rk.nextHalt else None,
            exceptions=[
                ExceptionInfo(
                    type=e.type,
                    message=e.message,
                    diverted=e.diverted,
                    partially_cancelled=e.partiallyCancelled,
                    rescheduled=e.rescheduled,
                )
                for e in (rk.exceptions or [])
            ],
            route=[RailRadarMapper._to_schedule_stop(s) for s in (rk.route or [])],
            is_live=rk.isLive,
        )

    @staticmethod
    def map_route(rk) -> RouteGeometry:
        if RailRadarMapper._is_dict(rk):
            stops = []
            if rk.get("stops"):
                stops = [RailRadarMapper._to_route_stop_from_route(s) for s in rk["stops"]]
            elif rk.get("route"):
                stops = [RailRadarMapper._to_route_stop(s) for s in rk["route"]]
            return RouteGeometry(
                train_number=rk.get("trainNumber") or rk.get("train_number", ""),
                stops=stops,
                coordinates=rk.get("coordinates", []),
                total_distance_km=rk.get("total_distance_km", 0.0),
                format=rk.get("format"),
                geojson=rk.get("geojson"),
                polyline=rk.get("polyline"),
            )

        stops = []
        if rk.stops:
            stops = [RailRadarMapper._to_route_stop_from_route(s) for s in rk.stops]
        elif rk.route:
            stops = [RailRadarMapper._to_route_stop(s) for s in rk.route]
        return RouteGeometry(
            train_number=rk.trainNumber or rk.train_number or "",
            stops=stops,
            coordinates=rk.coordinates,
            total_distance_km=rk.total_distance_km,
            format=rk.format,
            geojson=rk.geojson,
            polyline=rk.polyline,
        )

    @staticmethod
    def map_station_board(rk) -> list[StationBoardEntry]:
        if RailRadarMapper._is_dict(rk):
            entries = []
            for t in (rk.get("trains") or []):
                if RailRadarMapper._is_dict(t):
                    train_data = t.get("train", {})
                    if RailRadarMapper._is_dict(train_data):
                        train_number = str(train_data.get("number", ""))
                        train_name = train_data.get("name", "")
                        source = train_data.get("source", {})
                        if RailRadarMapper._is_dict(source):
                            source = source.get("code", "")
                        else:
                            source = ""
                        destination = train_data.get("destination", {})
                        if RailRadarMapper._is_dict(destination):
                            destination = destination.get("code", "")
                        else:
                            destination = ""
                    else:
                        train_number = ""
                        train_name = ""
                        source = ""
                        destination = ""
                    stop = t.get("stop")
                    if RailRadarMapper._is_dict(stop):
                        departure_time = stop.get("departure")
                        arrival_time = stop.get("arrival")
                    else:
                        departure_time = None
                        arrival_time = None
                    platform = None
                    status = "ON_TIME"
                    delay_minutes = 0
                    live_type = None
                    live_data = t.get("live")
                    if live_data and RailRadarMapper._is_dict(live_data):
                        platform = live_data.get("platform")
                        status = live_data.get("type", "ON_TIME")
                        delay_minutes = live_data.get("delayMinutes", 0)
                        live_type = status
                    entries.append(StationBoardEntry(
                        train_number=train_number,
                        train_name=train_name,
                        source=source,
                        destination=destination,
                        departure_time=departure_time,
                        arrival_time=arrival_time,
                        platform=platform,
                        status=status,
                        delay_minutes=delay_minutes,
                        sequence=stop.get("sequence") if stop and RailRadarMapper._is_dict(stop) else None,
                        stop_type=stop.get("stopType") if stop and RailRadarMapper._is_dict(stop) else None,
                        live_type=live_type,
                        live_status=live_data,
                    ))
            return entries

        entries = []
        for t in rk.trains:
            if t.train:
                train_number = str(t.train.number)
                train_name = t.train.name
                source = t.train.source.code if t.train.source else ""
                destination = t.train.destination.code if t.train.destination else ""
            else:
                train_number = ""
                train_name = ""
                source = ""
                destination = ""
            stop = t.stop
            departure_time = stop.departure if stop else None
            arrival_time = stop.arrival if stop else None
            platform = None
            status = "ON_TIME"
            delay_minutes = 0
            live_type = None
            if t.live:
                platform = t.live.get("platform") if isinstance(t.live, dict) else None
                status = t.live.get("type", "ON_TIME") if isinstance(t.live, dict) else "ON_TIME"
                delay_minutes = t.live.get("delayMinutes", 0) if isinstance(t.live, dict) else 0
                live_type = status
            entries.append(StationBoardEntry(
                train_number=train_number,
                train_name=train_name,
                source=source,
                destination=destination,
                departure_time=departure_time,
                arrival_time=arrival_time,
                platform=platform,
                status=status,
                delay_minutes=delay_minutes,
                sequence=stop.sequence if stop else None,
                stop_type=stop.stopType if stop else None,
                live_type=live_type,
                live_status=t.live,
            ))
        return entries

    @staticmethod
    def map_train_details(rk) -> TrainDetails:
        if RailRadarMapper._is_dict(rk):
            train_data = rk.get("train", {})
            if RailRadarMapper._is_dict(train_data):
                source = RailRadarMapper._to_station_info(train_data.get("source", {}))
                dest = RailRadarMapper._to_station_info(train_data.get("destination", {}))
                run_days = train_data.get("runDays") or train_data.get("runs_days", [])
                schedule = train_data.get("route") or train_data.get("schedule", [])
                return TrainDetails(
                    number=train_data.get("number", ""),
                    name=train_data.get("name", ""),
                    train_type=train_data.get("type", ""),
                    source=source,
                    destination=dest,
                    category=train_data.get("category"),
                    classes_available=train_data.get("classes_available", []),
                    schedule=[RailRadarMapper._to_schedule_stop(s) for s in schedule],
                    distance_km=train_data.get("distance_km") or train_data.get("distance"),
                    duration_minutes=train_data.get("duration_minutes") or train_data.get("duration"),
                    runs_days=run_days,
                    avg_speed=train_data.get("avgSpeed") or train_data.get("avg_speed"),
                    max_speed=train_data.get("maxSpeed") or train_data.get("max_speed"),
                    total_halts=train_data.get("totalHalts") or train_data.get("total_halts"),
                    return_train=train_data.get("returnTrain"),
                    coach_position=train_data.get("coachPosition"),
                )
            return TrainDetails(
                number="",
                name="",
                train_type="",
                source=Station(code="", name=""),
                destination=Station(code="", name=""),
            )

        source = RailRadarMapper._to_station_info(rk.train.source)
        dest = RailRadarMapper._to_station_info(rk.train.destination)
        run_days = rk.train.runDays or rk.train.runs_days
        schedule = rk.route or rk.schedule
        return TrainDetails(
            number=rk.train.number,
            name=rk.train.name,
            train_type=rk.train.type,
            source=source,
            destination=dest,
            category=rk.train.category,
            classes_available=rk.train.classes_available,
            schedule=[RailRadarMapper._to_schedule_stop(s) for s in schedule],
            distance_km=rk.train.distance_km or rk.train.distance,
            duration_minutes=rk.train.duration_minutes or rk.train.duration,
            runs_days=run_days,
            avg_speed=rk.train.avgSpeed or rk.train.avg_speed,
            max_speed=rk.train.maxSpeed or rk.train.max_speed,
            total_halts=rk.train.totalHalts or rk.train.total_halts,
            return_train=rk.train.returnTrain,
            coach_position=rk.train.coachPosition,
        )

    @staticmethod
    def map_station_lookup(rk) -> StationLookupResult:
        if RailRadarMapper._is_dict(rk):
            return StationLookupResult(
                station_code=rk.get("code", ""),
                station_name=rk.get("name", ""),
                zone=rk.get("zone"),
                state=rk.get("state"),
                latitude=rk.get("latitude"),
                longitude=rk.get("longitude"),
            )
        return StationLookupResult(
            station_code=rk.code,
            station_name=rk.name,
            zone=rk.zone,
            state=rk.state,
            latitude=rk.latitude,
            longitude=rk.longitude,
        )

    @staticmethod
    def map_station_search(rk) -> StationSearchResponse:
        if RailRadarMapper._is_dict(rk):
            stations = [RailRadarMapper.map_station_lookup(s) for s in (rk.get("stations") or [])]
            return StationSearchResponse(stations=stations, total=rk.get("total", len(stations)))
        return StationSearchResponse(
            stations=[RailRadarMapper.map_station_lookup(s) for s in rk.stations],
            total=rk.total,
        )

    @staticmethod
    def map_train_lookup(data) -> dict:
        if RailRadarMapper._is_dict(data):
            return data
        return data.data if hasattr(data, 'data') else {}

    @staticmethod
    def map_station_lookup_all(data) -> dict:
        if RailRadarMapper._is_dict(data):
            return data
        return data.data if hasattr(data, 'data') else {}
