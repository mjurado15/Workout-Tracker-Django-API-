def serialize_datetime(datetime):
    return datetime.isoformat()[:-6] + "Z"
