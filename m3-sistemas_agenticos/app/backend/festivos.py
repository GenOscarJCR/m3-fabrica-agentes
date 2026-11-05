"""Calendario de festivos oficiales y cálculo de días hábiles para vacaciones."""

from datetime import date, timedelta

FESTIVOS: dict[int, set[date]] = {
    2026: {
        date(2026, 1, 1),
        date(2026, 2, 2),
        date(2026, 3, 16),
        date(2026, 5, 1),
        date(2026, 9, 16),
        date(2026, 11, 16),
        date(2026, 12, 25),
    },
    2027: {
        date(2027, 1, 1),
        date(2027, 2, 1),
        date(2027, 3, 15),
        date(2027, 5, 1),
        date(2027, 9, 16),
        date(2027, 11, 15),
        date(2027, 12, 25),
    },
}


def es_dia_habil(fecha: date) -> bool:
    if fecha.weekday() >= 5:
        return False
    return fecha not in FESTIVOS.get(fecha.year, set())


def dias_habiles_en_periodo(inicio: date, fin: date) -> int:
    dias = 0
    fecha = inicio
    while fecha <= fin:
        if es_dia_habil(fecha):
            dias += 1
        fecha += timedelta(days=1)
    return dias
