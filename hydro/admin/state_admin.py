from django.contrib import admin
from hydro.models import State

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'initials')
    search_fields = ('name', 'initials')
    ordering = ('name',)