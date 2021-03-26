from dataclasses import dataclass
import typing


@dataclass(frozen=True)
class ComponentFrame:
    component: str
    frame: int
    timestamp: str
    reachable: bool
    responseTime: float


@dataclass(frozen=True)
class ComponentConfig:
    id: str
    name: str
    baseUrl: str
    statusEndpoint: str
    frequency: str
    systemId: str
    ref: str
    expectedTime: str
    timeout: str
    deleteAfter: str


@dataclass(frozen=True)
class SystemConfig:
    id: str
    name: str
    ref: str


@dataclass(frozen=True)
class System:
    system: str
    name: str
    ref: str


@dataclass(frozen=True)
class Component:
    component: str
    name: str
    frequency: str
    baseUrl: str
    statusEndpoint: str
    system: str
    ref: str
    expectedTime: str
    timeout: str


@dataclass(frozen=True)
class DtoComponentFrame:
    id: int
    timestamp: str
    reachable: bool
    responseTime: float


@dataclass(frozen=True)
class DtoSystem:
    name: str
    ref: str


@dataclass(frozen=True)
class DtoComponent:
    name: str
    frequency: str
    system: str
    ref: str
    expectedTime: str
    timeout: str
    frames: typing.List[DtoComponentFrame]


@dataclass(frozen=True)
class DtoMonitorData:
    components: typing.List[DtoComponent]
    systems: typing.List[DtoSystem]
