from django.contrib import admin
from hydro.models import PrecipitationRecord


@admin.register(PrecipitationRecord)
class PrecipitationRecordAdmin(admin.ModelAdmin):
    list_display = ('station', 'date', 'value', 'is_gap')
    list_filter = ('is_gap', 'date', 'station__state')
    search_fields = ('station__code', 'station__name')
    ordering = ('-date',)
    date_hierarchy = 'date'
    
    # raw_id_fields evita carregar milhares de estações em um <select> HTML, garantindo performance no Admin
    raw_id_fields = ('station',)
    list_per_page = 50