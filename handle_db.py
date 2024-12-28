from base.models import AvailableTime
from datetime import datetime

# Fetch all rows
all_times = AvailableTime.objects.all()

# Delete rows where start_time is not a valid datetime
for time in all_times:
    try:
        if time.start_time > time.end_time:
            time.delete()
    except (ValueError, TypeError):
        # Handle invalid datetime format or NoneType
        time.delete()