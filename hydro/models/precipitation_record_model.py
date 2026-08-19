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

    value_ana = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Precipitação ANA (mm)'
    )
    is_gap_ana = models.BooleanField(
        default=False,
        verbose_name='Falha ANA?'
    )

    value_inmet = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Precipitação INMET (mm)'
    )
    is_gap_inmet = models.BooleanField(
        default=True, # Por padrão assumimos falha até o pipeline preencher
        verbose_name='Falha INMET?'
    )

    class Meta:
        verbose_name = 'Registro Pluviométrico'
        verbose_name_plural = 'Registros Pluviométricos'
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(
                fields=['station', 'date'],
                name='unique_station_date_precipitation'
            )
        ]
        indexes = [
            models.Index(fields=['station', 'date']),
            models.Index(fields=['is_gap_ana']),
            models.Index(fields=['is_gap_inmet']),
        ]

    def __str__(self):
        return f"{self.station.code_ana} | {self.date}"