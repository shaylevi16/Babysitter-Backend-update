from django.contrib import admin
from .models import Babysitter, Meetings, Requests
from .models import Parents
from .models import Kids
from .models import Reviews
from .models import AvailableTime



admin.site.register(Kids)
admin.site.register(Meetings)
admin.site.register(Reviews)
admin.site.register(AvailableTime)
admin.site.register(Requests)
admin.site.register(Parents)
admin.site.register(Babysitter)



