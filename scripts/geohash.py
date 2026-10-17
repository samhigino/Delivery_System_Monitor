# Tabela de Base32 para consultar
code_table = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'j', 'k', 'm', 'n', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

# Função para obter o geohash de uma coordenada
def geohash_encode(lat:float, lon:float, maxlevel=8):
    is_odd = False
    latmin, latmax = [-90.0, 90.0]
    lonmin, lonmax = [-180.0, 180.0]
    latoffset = 0.0
    lonoffset = 0.0
    prefix = ""
    bitsequence = 0

    for i in range(maxlevel):
        for j in range(5):
            
            bitsequence = bitsequence << 1
            is_odd = not is_odd

            if is_odd:     # Longitude
                lonmax /= 2
                lonmin /= 2
                if lon - lonoffset >= 0.0:
                    bitsequence |= 1
                    lonoffset += lonmax
                else:
                    lonoffset += lonmin

            else:           # Latitude
                latmax /= 2
                latmin /= 2
                if lat - latoffset >= 0.0:
                    bitsequence |= 1
                    latoffset += latmax
                else:
                    latoffset += latmin

        prefix += code_table[bitsequence]
        bitsequence = 0

    return prefix

# Função para obter as coordenadas a partir de um geohash
def geohash_decode(geohash):
    lat = 0.0
    lon = 0.0
    latmin, latmax = [-90.0, 90.0]
    lonmin, lonmax = [-180.0, 180.0]
    is_odd = True

    for c in geohash:
        idx = code_table.index(c)

        i = 4
        while i >= 0:
            val = (idx & (1 << i)) >> i     # extrai o bit de interesse para a análise

            if is_odd:  # Longitude
                lonmax /= 2
                lonmin /= 2
                if val > 0:
                    lon += lonmax
                else:
                    lon += lonmin

            else:       # Latitude
                latmax /= 2
                latmin /= 2
                if val > 0:
                    lat += latmax
                else:
                    lat += latmin

            is_odd = not is_odd
            i -= 1

    return lat, lon

# Função para achar a vizinhança de algum geohash
def geohash_neigh(geohash, x=1, y=0, levels=8):
    
    return
