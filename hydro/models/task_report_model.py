from django.db import models
from django.conf import settings


class TaskReport(models.Model):

    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pendente'
        PROCESSING = 'PROCESSING', 'Processando'
        SUCCESS = 'SUCCESS', 'Concluído'
        FAILED = 'FAILED', 'Erro'

    task_id = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='ID da Tarefa (Celery)'
    )
    task_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Nome da Tarefa / Processo'
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        verbose_name='Status'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='task_reports',
        verbose_name='Usuário Solicitante'
    )
    result_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='Resultado / Detalhes'
    )
    error_log = models.TextField(
        blank=True,
        null=True,
        verbose_name='Log de Erro'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Atualização'
    )

    class Meta:
        verbose_name = 'Relatório de Tarefa'
        verbose_name_plural = 'Relatórios de Tarefas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task_id']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        nome = self.task_name or self.task_id
        user_str = self.user.username if self.user else 'Sistema/Anônimo'
        return f"[{self.get_status_display()}] {nome} ({user_str})"