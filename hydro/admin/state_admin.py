from django.contrib import admin
from hydro.models import State

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )
    ordering = ('name',)