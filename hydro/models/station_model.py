from django.contrib.gis.db import models

class Station(models.Model):
    """
    Modelo para armazenar as Estações Meteorológicas/Pluviométricas vindas da ANA/hydrobr.
    Utiliza PostGIS para armazenamento geoespacial.
    """
    
    # -----------------------------------------------------
    # 1. Identificação e Localização Básica
    # -----------------------------------------------------
    # A API usa o 'Code' como identificador único. É perfeito para ser a Chave Primária.
    code = models.CharField(max_length=20, primary_key=True, verbose_name="Código ANA")
    name = models.CharField(max_length=255, verbose_name="Nome da Estação")
    station_type = models.CharField(max_length=50, null=True, blank=True, verbose_name="Tipo")
    sub_basin = models.CharField(max_length=100, null=True, blank=True, verbose_name="Sub-Bacia")
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name="Cidade")
    state = models.CharField(max_length=2, null=True, blank=True, verbose_name="Estado")
    responsible = models.CharField(max_length=150, null=True, blank=True, verbose_name="Responsável")

    # -----------------------------------------------------
    # 2. Dados Geoespaciais (PostGIS)
    # -----------------------------------------------------
    # Substitui as colunas isoladas de 'Latitude' e 'Longitude' do DataFrame.
    # SRID 4326 é o padrão mundial (WGS 84), o mesmo usado pelo GPS e Google Maps.
    geom = models.PointField(srid=4326, verbose_name="Geometria (Lat/Lon)")

    # -----------------------------------------------------
    # 3. Metadados Temporais e Qualidade da Série (API)
    # -----------------------------------------------------
    # Como a API pode retornar valores nulos ou faltantes para estatísticas, 
    # todos estes campos permitem null=True e blank=True.
    start_date = models.DateField(null=True, blank=True, verbose_name="Data Inicial (StartDate)")
    end_date = models.DateField(null=True, blank=True, verbose_name="Data Final (EndDate)")
    
    nyd = models.FloatField(null=True, blank=True, verbose_name="Anos com Dados (NYD)")
    md = models.FloatField(null=True, blank=True, verbose_name="Dados Faltantes/Missing (MD)")
    n_ywomd = models.FloatField(null=True, blank=True, verbose_name="Anos sem Falhas (N_YWOMD)")
    ywmd = models.FloatField(null=True, blank=True, verbose_name="Anos com Falhas (YWMD)")

    # -----------------------------------------------------
    # 4. Auditoria Interna do Sistema
    # -----------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado no Sistema em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    class Meta:
        db_table = 'hydro_station'
        verbose_name = 'Estação Meteorológica'
        verbose_name_plural = 'Estações Meteorológicas'
        ordering = ['state', 'name']

    def __str__(self):
        return f"{self.code} - {self.name} ({self.state})"

    # Propriedades auxiliares para facilitar o uso na sua interface Web ou API futura
    @property
    def latitude(self):
        return self.geom.y if self.geom else None

    @property
    def longitude(self):
        return self.geom.x if self.geom else None