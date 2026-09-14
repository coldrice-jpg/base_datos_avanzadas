"""Excepciones de dominio para operaciones de negocio."""

class TiendaError(Exception):
    """Excepción base para el dominio de la tienda."""


class StockInsuficienteError(TiendaError):
    """Lanzada cuando se intenta vender una cantidad mayor a la disponible."""


class EntidadNoEncontradaError(TiendaError):
    """Lanzada cuando un registro consultado no existe en ZODB."""


class ValidacionDatosError(TiendaError):
    """Lanzada cuando los datos de entrada no cumplen las reglas."""