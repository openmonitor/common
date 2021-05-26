from dataclasses import dataclass
from enum import Enum
import typing


class Version(Enum):
    V1 = 'v1',
    V2 = 'v2',

class TimeUnit(Enum):
    MILLISECOND = 'ms'
    SECOND = 's'
    MINUTE = 'm'
    HOUR = 'h'
    DAY = 'd'

class TimeUnitMilliseconds(Enum):
    MILLISECOND = 1
    SECOND = 60
    MINUTE = 3600
    HOUR = 216000
    DAY = 5184000

class TimeUnitPhoenic(Enum):
    MILLISECOND = 'milliseconds'
    SECOND = 'seconds'
    MINUTE = 'minutes'
    HOUR = 'hours'
    DAY = 'days'

@dataclass(frozen=True)
class TimeDetail:
    value: int
    unit: TimeUnit

    def as_string(self):
        return self.value + self.unit.value

    def _unit_to_phonetic_name(
        self,
        unit: TimeUnit,
    ):
        return TimeUnitPhoenic[unit.name].value

    def as_interval(self):
        return f'{self.value} {self._unit_to_phonetic_name(unit=self.unit)}'

    def as_ms(self):
        return int(self.value * TimeUnitMilliseconds[self.unit.name].value)

@dataclass(frozen=True)
class Metric:
    id: str
    endpoint: str
    frequency: TimeDetail
    expectedTime: TimeDetail
    timeout: TimeDetail
    deleteAfter: TimeDetail
    authToken: str
    baseUrl: str

@dataclass(frozen=True)
class Component:
    id: str
    name: str
    systemId: str
    baseUrl: str
    ref: str
    authToken: str
    metrics: typing.Union[typing.List[Metric], None]

@dataclass(frozen=True)
class System:
    id: str
    name: str
    ref: str

@dataclass(frozen=True)
class Config:
    components: typing.List[Component]
    systems: typing.List[System]
    version: Version

@dataclass(frozen=True)
class Result:
    metricId: str
    componentId: str
    value: typing.Union[str, None]
    timeout: bool
    timestamp: str
    responseTime: int
