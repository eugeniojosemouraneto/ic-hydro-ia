from django.contrib.gis.db import models

from .state_model import State

class Station(models.Model):
    """
    Modelo para armazenar as Estações Meteorológicas/Pluviométricas vindas da ANA/hydrobr.
    Utiliza PostGIS para armazenamento geoespacial.
    """

    code_ana = models.CharField(max_length=20, primary_key=True, verbose_name="Código ANA")
    code_inmet = models.CharField(max_length=20, null=True, blank=True, verbose_name="Código INMET")
    
    name = models.CharField(max_length=255, verbose_name="Nome da Estação")
    station_type = models.CharField(max_length=50, null=True, blank=True, verbose_name="Tipo")
    sub_basin = models.CharField(max_length=100, null=True, blank=True, verbose_name="Sub-Bacia")
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name="Cidade")
    state = models.ForeignKey(State, on_delete=models.CASCADE, blank=True, null=True)
    responsible = models.CharField(max_length=150, null=True, blank=True, verbose_name="Responsável")

    geom = models.PointField(srid=4326, verbose_name="Geometria (Lat/Lon)")

    start_date = models.DateField(null=True, blank=True, verbose_name="Data Inicial (StartDate)")
    end_date = models.DateField(null=True, blank=True, verbose_name="Data Final (EndDate)")
    
    nyd = models.FloatField(null=True, blank=True, verbose_name="Anos com Dados (NYD)")
    md = models.FloatField(null=True, blank=True, verbose_name="Dados Faltantes/Missing (MD)")
    n_ywomd = models.FloatField(null=True, blank=True, verbose_name="Anos sem Falhas (N_YWOMD)")
    ywmd = models.FloatField(null=True, blank=True, verbose_name="Anos com Falhas (YWMD)")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado no Sistema em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    class Meta:
        db_table = 'hydro_station'
        verbose_name = 'Estação Meteorológica'
        verbose_name_plural = 'Estações Meteorológicas'
        ordering = ['state', 'name']

    def __str__(self):
        inmet_str = f" | INMET: {self.code_inmet}" if self.code_inmet else ""
        return f"ANA: {self.code_ana}{inmet_str} - {self.name}"

    # Propriedades auxiliares para facilitar o uso na sua interface Web ou API futura
    @property
    def latitude(self):
        return self.geom.y if self.geom else None

    @property
    def longitude(self):
        return self.geom.x if self.geom else None