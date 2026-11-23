"""Map-generator bookkeeping for the Old Quarry's rebuilt camp."""


def quarry_shelter(m, x, z):
    if not hasattr(m, "quarry_shelters"):
        m.quarry_shelters = []
    m.quarry_shelters.append((x, z))
    # Poles and rear edge retain their footprint. The front of each tent opens.
    m.walls.extend([(x, z), (x + 5, z)] + [(px, z + 4) for px in range(x, x + 6)])
