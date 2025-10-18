import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"


class ImageStatus(str, enum.Enum):
    new = "new"
    processing = "processing"
    processed = "processed"
    failed = "failed"


class QueryType(str, enum.Enum):
    predict = "predict"
    search = "search"


class QueryStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
