import numpy as np

# Gera n entregadores ao redor de uma coordenada especificada e retorna um vetor de suas coordenadas - formato (n, 2)
def generate_delivery_single(lat, lon, n=10, desv=1.0):
    rng = np.random.default_rng()

    randlat = rng.normal(loc=lat, scale=desv, size=n)
    randlon = rng.normal(loc=lon, scale=desv, size=n)

    locations = np.column_stack((randlat, randlon))

    return locations