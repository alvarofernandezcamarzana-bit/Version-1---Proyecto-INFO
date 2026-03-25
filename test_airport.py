"""Pruebas sencillas para airport.py."""

import os

from airport import (
    Airport,
    AddAirport,
    LoadAirports,
    MapAirports,
    PlotAirports,
    PrintAirport,
    RemoveAirport,
    SaveSchengenAirports,
    SetSchengen,
)


def _sample_file():
    filename = "sample_airports.txt"
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as handler:
            handler.write(
                """CODE LAT LON
BIKF N635906 W0223620
CYUL N452805 W0734429
CYYZ N434038 W0793750
DAAG N364138 E0031252
EBAW N511122 E0042737
"""
            )
    return filename


def run_demo():
    filename = _sample_file()
    airports = LoadAirports(filename)
    print("\nAeropuertos cargados:")
    for airport in airports:
        PrintAirport(airport)

    print("\nAñadiendo LEBL y calculando Schengen:")
    new_airport = Airport("LEBL", 41.297445, 2.0832941)
    SetSchengen(new_airport)
    AddAirport(airports, new_airport)
    for airport in airports:
        SetSchengen(airport)
        PrintAirport(airport)

    print("\nGuardando aeropuertos Schengen:")
    SaveSchengenAirports(airports, "schengen_airports.txt")

    print("\nQuitando CYUL:")
    RemoveAirport(airports, "CYUL")
    for airport in airports:
        PrintAirport(airport)

    if os.environ.get("AIRPORT_TEST_VISUAL") == "1":
        PlotAirports(airports)
        MapAirports(airports)
    else:
        print("\nPruebas visuales desactivadas (pon AIRPORT_TEST_VISUAL=1 para verlas)")


if __name__ == "__main__":
    run_demo()
