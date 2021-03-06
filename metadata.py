import re
from functools import lru_cache
import pandas as pd


# 加载静态数据
country_code = pd.read_csv("CountryCode.csv")
china_area_code = pd.read_csv("ChinaAreaCode.csv")
china_area_code["code"] = china_area_code["code"].astype(str)
china_area_code["is_province"] = china_area_code["code"].map(
    lambda x: bool(re.match("\\d{2}0000$", x)))
china_area_code["province_code"] = china_area_code["code"].map(
    lambda x: re.sub("\\d{4}$", "0000", x))


@lru_cache(maxsize=128)
def get_country_code(name):
    result = country_code.loc[country_code["name"].isin([name])]["code"]
    if (len(result.values) > 0):
        return result.values[0]
    return ""


@lru_cache(maxsize=64)
def get_china_province_code(province, provinceCode=None):
    if provinceCode:
        return provinceCode
    if not province:
        return ""
    result = china_area_code.loc[china_area_code["is_province"] & china_area_code["name"].str.contains(province)]["code"]
    if (len(result.values) > 0):
        return result.values[0]
    return ""


@lru_cache(maxsize=1024)
def get_china_city_code(provinceCode, city, cityCode=None):
    if cityCode:
        return cityCode
    if not city or not provinceCode:
        return ""
    result = china_area_code.loc[china_area_code["province_code"].isin([provinceCode]) & ~china_area_code["is_province"] & china_area_code["name"].isin([city])]["code"]
    if (len(result.values) > 0):
        return result.values[0]
    result = china_area_code.loc[china_area_code["province_code"].isin([provinceCode]) & ~china_area_code["is_province"] & china_area_code["name"].str.contains(city)]["code"]
    if (len(result.values) > 0):
        return result.values[0]

    for i in range(1, len(city)):
        fuzzy_name = city[:-i] + ".*" + ".*".join(city[-i:])
        result = china_area_code.loc[china_area_code["province_code"].isin([provinceCode]) & ~china_area_code["is_province"] & china_area_code["name"].str.match(fuzzy_name)]["code"]
        if (len(result.values) > 0):
            # print(f"""{province_code} {fuzzy_name} -> {",".join(result.values)}""")
            return result.values[0]

    return ""


@lru_cache(maxsize=1024)
def get_china_area_name(code, name):
    if not code:
        return name
    result = china_area_code.loc[china_area_code["code"].isin([code])]["name"]
    if (len(result.values) > 0):
        return result.values[0]
    return name
