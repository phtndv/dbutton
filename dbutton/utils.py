def apply_filters(data, filters):
    """
    data    : iterable de dicts
    filters : dict {campo: valor}
    devuelve una lista filtrada
    """
    if not filters:
        return list(data)
    result = []
    for item in data:
        match = True
        for key, val in filters.items():
            if str(item.get(key, "")).lower() != str(val).lower():
                match = False
                break
        if match:
            result.append(item)
    return result
def paginate(data, page, page_size):
    """
    data      : lista ya filtrada
    page      : número de página (1‑based)
    page_size : cuántos registros por página
    devuelve (slice, total_pages)
    """
    total = len(data)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    end = start + page_size
    return data[start:end], total_pages
