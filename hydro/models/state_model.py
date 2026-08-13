from django.contrib.gis.db import models

class State(models.Model):
    """
    Modelo para armazenar os Estados do Brasil, que será vinculada a estação 
    Meteorológico utilizando também para filtros de buscas.
    """

    name = models.CharField(max_length=50, verbose_name="Estado")

    def __str__(self):
        return self.name