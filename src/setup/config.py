def use_proper_city_name(city_name: str) -> str:

    if "_" in city_name:
        return city_name.replace("_", "").title()
    else: 
        return city_name.title()
