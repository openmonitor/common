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

@dataclass(frozen=True)
class TimeDetail:
    value: int
    unit: TimeUnit

    def as_string(self):
        return self.value + self.unit

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
