"""Funciones básicas para la versión 1 del ProjectoAeropuerto."""

import os
import webbrowser

import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt


SCHENGEN_PREFIXES = [
    "LO",
    "EB",
    "LK",
    "LC",
    "EK",
    "EE",
    "EF",
    "LF",
    "ED",
    "LG",
    "EH",
    "LH",
    "BI",
    "LI",
    "EV",
    "EY",
    "EL",
    "LM",
    "EN",
    "EP",
    "LP",
    "LZ",
    "LJ",
    "LE",
    "ES",
    "LS",
]


ERROR_EMPTY_LIST = -1
ERROR_NOT_FOUND = -2


class Airport:
    def __init__(self, code, latitude, longitude):
        self.code = code.strip().upper()
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.schengen = False


def _normalize_code(code):
    return code.strip().upper()


def IsSchengenAirport(code):
    if not code:
        return False
    prefix = _normalize_code(code)[:2]
    for valid in SCHENGEN_PREFIXES:
        if prefix == valid:
            return True
    return False


def SetSchengen(airport):
    airport.schengen = IsSchengenAirport(airport.code)


def PrintAirport(airport):
    print(
        f"{airport.code} -> lat={airport.latitude:.6f}, lon={airport.longitude:.6f}, "
        f"schengen={'yes' if airport.schengen else 'no'}"
    )


def _sexagesimal_to_decimal(coord):
    coord = coord.strip()
    if not coord:
        return None
    direction = coord[0].upper()
    digits = coord[1:]
    if not digits.isdigit():
        return None
    if len(digits) == 6:
        deg = int(digits[:2])
        minutes = int(digits[2:4])
        seconds = int(digits[4:])
    else:
        deg = int(digits[:3])
        minutes = int(digits[3:5])
        seconds = int(digits[5:])
    decimal = deg + minutes / 60 + seconds / 3600
    if direction in ("S", "W"):
        decimal = -decimal
    return decimal


def _decimal_to_sexagesimal(value, is_latitude):
    value = float(value)
    if is_latitude:
        direction = "N" if value >= 0 else "S"
    else:
        direction = "E" if value >= 0 else "W"
    value = abs(value)
    degrees = int(value)
    remainder = (value - degrees) * 60
    minutes = int(remainder)
    seconds = int(round((remainder - minutes) * 60))
    if seconds == 60:
        seconds = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        degrees += 1
    if is_latitude:
        body = f"{degrees:02d}{minutes:02d}{seconds:02d}"
    else:
        body = f"{degrees:03d}{minutes:02d}{seconds:02d}"
    return direction + body


def LoadAirports(filename):
    airports = []
    if not os.path.exists(filename):
        return airports
    with open(filename, "r", encoding="utf-8") as handler:
        header_consumed = False
        for raw_line in handler:
            line = raw_line.strip()
            if not line:
                continue
            if not header_consumed:
                header_consumed = True
                continue
            parts = line.split()
            if len(parts) < 3:
                continue
            code = _normalize_code(parts[0])
            lat = _sexagesimal_to_decimal(parts[1])
            lon = _sexagesimal_to_decimal(parts[2])
            if lat is None or lon is None:
                continue
            airport = Airport(code, lat, lon)
            airports.append(airport)
    return airports


def SaveSchengenAirports(airports, filename):
    schengen_airports = []
    for airport in airports:
        if airport.schengen:
            schengen_airports.append(airport)
    if not schengen_airports:
        return ERROR_EMPTY_LIST
    with open(filename, "w", encoding="utf-8") as handler:
        handler.write("CODE LAT LON\n")
        for airport in schengen_airports:
            lat_code = _decimal_to_sexagesimal(airport.latitude, True)
            lon_code = _decimal_to_sexagesimal(airport.longitude, False)
            handler.write(f"{airport.code} {lat_code} {lon_code}\n")
    return len(schengen_airports)


def AddAirport(airports, airport):
    airport.code = _normalize_code(airport.code)
    for existing in airports:
        if existing.code == airport.code:
            return False
    airports.append(airport)
    return True


def RemoveAirport(airports, code):
    code = _normalize_code(code)
    for index in range(len(airports)):
        if airports[index].code == code:
            airports.pop(index)
            return index
    return ERROR_NOT_FOUND


def PlotAirports(airports):
    if not airports:
        print("No hay aeropuertos para mostrar")
        return
    schengen_count = 0
    for airport in airports:
        if airport.schengen:
            schengen_count += 1
    non_schengen_count = len(airports) - schengen_count
    plt.figure(figsize=(5, 4))
    plt.bar(["Aeropuertos"], [schengen_count], label="Schengen", color="#2ecc71")
    plt.bar(
        ["Aeropuertos"],
        [non_schengen_count],
        bottom=[schengen_count],
        label="No Schengen",
        color="#e67e22",
    )
    plt.ylabel("Aeropuertos")
    plt.title("Aeropuertos Schengen vs No Schengen")
    plt.legend()
    plt.tight_layout()
    plt.show()


def MapAirports(airports, output=None):
    if not airports:
        print("No hay aeropuertos para mostrar en el mapa")
        return None
    if output is None:
        output = "airports_map.kml"
    lines = [
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
        "<kml xmlns=\"http://www.opengis.net/kml/2.2\">",
        "  <Document>",
        "    <Style id=\"schengen\">",
        "      <IconStyle>",
        "        <color>ff33cc33</color>",
        "        <scale>1.2</scale>",
        "        <Icon>",
        "          <href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href>",
        "        </Icon>",
        "      </IconStyle>",
        "    </Style>",
        "    <Style id=\"nonschengen\">",
        "      <IconStyle>",
        "        <color>ff3366ff</color>",
        "        <scale>1.2</scale>",
        "        <Icon>",
        "          <href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href>",
        "        </Icon>",
        "      </IconStyle>",
        "    </Style>",
    ]
    for airport in airports:
        style = "schengen" if airport.schengen else "nonschengen"
        lines.append("    <Placemark>")
        lines.append(f"      <name>{airport.code}</name>")
        lines.append(f"      <styleUrl>#{style}</styleUrl>")
        lines.append(
            f"      <description>Lat {airport.latitude:.4f}, Lon {airport.longitude:.4f}</description>"
        )
        lines.append("      <Point>")
        lines.append(f"        <coordinates>{airport.longitude},{airport.latitude},0</coordinates>")
        lines.append("      </Point>")
        lines.append("    </Placemark>")
    lines.append("  </Document>")
    lines.append("</kml>")
    content = "\n".join(lines)
    with open(output, "w", encoding="utf-8") as handler:
        handler.write(content)
    full_path = os.path.abspath(output)
    url = "file:///" + full_path.replace("\\", "/")
    webbrowser.open(url)
    return output


__all__ = [
    "Airport",
    "IsSchengenAirport",
    "SetSchengen",
    "PrintAirport",
    "LoadAirports",
    "SaveSchengenAirports",
    "AddAirport",
    "RemoveAirport",
    "PlotAirports",
    "MapAirports",
    "ERROR_EMPTY_LIST",
    "ERROR_NOT_FOUND",
]
