
# Tabela Base32 do Geohash
code_table = [
    '0', '1', '2', '3', '4', '5', '6', '7',
    '8', '9', 'b', 'c', 'd', 'e', 'f', 'g',
    'h', 'j', 'k', 'm', 'n', 'p', 'q', 'r',
    's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
]


# Codifica latitude e longitude em um Geohash
def geohash_encode(lat: float, lon: float, maxlevel=8):
    if not -90 <= lat <= 90:
        raise ValueError("Latitude deve estar entre -90 e 90.")

    if not -180 <= lon <= 180:
        raise ValueError("Longitude deve estar entre -180 e 180.")

    if not isinstance(maxlevel, int) or maxlevel < 1:
        raise ValueError("maxlevel deve ser um inteiro positivo.")

    latmin, latmax = -90.0, 90.0
    lonmin, lonmax = -180.0, 180.0

    geohash = ""
    bits = 0
    bit_count = 0
    is_lon = True

    for _ in range(maxlevel * 5):
        bits <<= 1

        if is_lon:
            meio = (lonmin + lonmax) / 2

            if lon >= meio:
                bits |= 1
                lonmin = meio
            else:
                lonmax = meio

        else:
            meio = (latmin + latmax) / 2

            if lat >= meio:
                bits |= 1
                latmin = meio
            else:
                latmax = meio

        is_lon = not is_lon
        bit_count += 1

        if bit_count == 5:
            geohash += code_table[bits]
            bits = 0
            bit_count = 0

    return geohash


# Decodifica o Geohash e retorna o centro da célula
def geohash_decode(geohash):
    if not isinstance(geohash, str) or not geohash:
        raise ValueError("O Geohash deve ser uma string não vazia.")

    latmin, latmax = -90.0, 90.0
    lonmin, lonmax = -180.0, 180.0

    is_lon = True

    for c in geohash.lower():
        if c not in code_table:
            raise ValueError(f"Caractere inválido no Geohash: {c}")

        valor = code_table.index(c)

        for i in range(4, -1, -1):
            bit = (valor >> i) & 1

            if is_lon:
                meio = (lonmin + lonmax) / 2

                if bit:
                    lonmin = meio
                else:
                    lonmax = meio

            else:
                meio = (latmin + latmax) / 2

                if bit:
                    latmin = meio
                else:
                    latmax = meio

            is_lon = not is_lon

    lat = (latmin + latmax) / 2
    lon = (lonmin + lonmax) / 2

    return lat, lon


# Retorna a célula vizinha.
# x: deslocamento horizontal
# y: deslocamento vertical
def geohash_neigh(geohash, x=0, y=0, levels=8):
    if not isinstance(levels, int) or levels < 1:
        raise ValueError("levels deve ser um inteiro positivo.")

    if len(geohash) < levels:
        raise ValueError("O Geohash é menor que levels.")

    if not isinstance(x, int) or not isinstance(y, int):
        raise ValueError("x e y devem ser inteiros.")

    geohash = geohash[:levels].lower()

    lat, lon = geohash_decode(geohash)

    total_bits = levels * 5
    lon_bits = (total_bits + 1) // 2
    lat_bits = total_bits // 2

    altura = 180.0 / (2 ** lat_bits)
    largura = 360.0 / (2 ** lon_bits)

    # Move pelo número de células solicitado
    lat += y * altura
    lon += x * largura

    # A latitude não pode ultrapassar os polos
    lat = max(-90.0, min(90.0, lat))

    # A longitude dá a volta ao cruzar o antimeridiano
    lon = ((lon + 180.0) % 360.0) - 180.0

    return geohash_encode(lat, lon, maxlevel=levels)
