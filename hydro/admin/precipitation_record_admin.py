from django.contrib import admin
from hydro.models import PrecipitationRecord

@admin.register(PrecipitationRecord)
class PrecipitationRecordAdmin(admin.ModelAdmin):
    """
    Painel de registros diários otimizado para alta volumetria.
    Exibe os dados lado a lado para facilitar a auditoria visual.
    """
    list_display = ('station', 'date', 'value_ana', 'is_gap_ana', 'value_inmet', 'is_gap_inmet')
    
    # Filtros laterais excelentes para caçar anomalias rapidamente
    list_filter = ('is_gap_ana', 'is_gap_inmet', 'date', 'station__state')
    
    # Pesquisa aceitando os dois códigos
    search_fields = ('station__code_ana', 'station__code_inmet', 'station__name')
    
    ordering = ('-date',)
    date_hierarchy = 'date'
    
    # raw_id_fields evita carregar milhares de estações em um <select> HTML, garantindo performance
    raw_id_fields = ('station',)
    list_per_page = 50