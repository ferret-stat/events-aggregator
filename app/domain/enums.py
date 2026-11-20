from enum import StrEnum


class EventStatus(StrEnum):
    REGISTRATION_CLOSED = "registration_closed"
    FINISHED = "finished"
    PUBLISHED = "published"


class SyncStatus(StrEnum):
    NEVER_SYNCED = "never_synced"
    SUCCESS = "success"
    FAILED = "failed"
