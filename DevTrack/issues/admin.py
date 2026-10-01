from django.contrib import admin
from .models import Issue, CriticalIssue, LowPriorityIssue

# Register your models here.
admin.site.register(Issue)
admin.site.register(CriticalIssue)
admin.site.register(LowPriorityIssue)
