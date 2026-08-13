from django.db import models
from hydro.models.station_model import Station


class PrecipitationRecord(models.Model):
    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name='precipitation_records',
        verbose_name='Estação'
    )
    date = models.DateField(
        verbose_name='Data da Leitura'
    )
    value = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Precipitação (mm)'
    )
    is_gap = models.BooleanField(
        default=False,
        verbose_name='Possui Falha?'
    )

    class Meta:
        verbose_name = 'Registro Pluviométrico'
        verbose_name_plural = 'Registros Pluviométricos'
        ordering = ['-date']
        constraints = [
            # Garante idempotência e impede duplicidade de data para a mesma estação
            models.UniqueConstraint(
                fields=['station', 'date'],
                name='unique_station_date_precipitation'
            )
        ]
        indexes = [
            # Índices cruciais para acelerar a busca do último registro e consultas temporais
            models.Index(fields=['station', 'date']),
            models.Index(fields=['is_gap']),
        ]

    def __str__(self):
        valor_str = f"{self.value} mm" if self.value is not None else "Sem dado"
        return f"{self.station.code} | {self.date} | {valor_str}"