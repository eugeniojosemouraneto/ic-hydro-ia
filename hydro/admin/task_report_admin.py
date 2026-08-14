from django.contrib import admin
from hydro.models import TaskReport


@admin.register(TaskReport)
class TaskReportAdmin(admin.ModelAdmin):
    list_display = ('task_name', 'task_id', 'status', 'user', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('task_id', 'task_name', 'user__username', 'result_message', 'error_log')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Identificação da Tarefa', {
            'fields': ('task_id', 'task_name', 'status', 'user')
        }),
        ('Resultados e Logs', {
            'fields': ('result_message', 'error_log')
        }),
        ('Auditoria Temporal', {
            'fields': ('created_at', 'updated_at')
        }),
    )