import csv
import math
import time

import pandas as pd
from bs4 import BeautifulSoup
import requests


def get_data():
    data = requests.get(
        "http://www.exercise4weightloss.com/weight-watchers-points.html"
    )
    soup = BeautifulSoup(data.content, "html.parser")
    rows = soup.find_all("tr")

    with open("./restaurant_foods.csv", "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(
            ["restaurant", "name", "serving", "fat", "carbs", "fiber", "protein"]
        )

        for i, row in enumerate(rows):
            link = row.find("a")
            if link is not None:
                href = link["href"]
                restaurant = link.text
                print("restaurant", restaurant)
                time.sleep(1)
                restaurant_info = requests.get(href)
                try:
                    restaurant_soup = BeautifulSoup(
                        restaurant_info.content, "html.parser"
                    )
                    desktop = restaurant_soup.find(class_="nonscriptTable")
                    head = desktop.find("thead")
                    header_row = head.find("tr")
                    columns = header_row.find_all("th")
                    name_idx = None
                    serv_idx = None
                    fat_idx = None
                    fiber_idx = None
                    protein_idx = None
                    carb_idx = None
                    for i, item in enumerate(columns):
                        _txt = item.text.strip()
                        if _txt == "Menu Item":
                            name_idx = i
                        elif _txt == "Serv":
                            serv_idx = i
                        elif _txt == "Tfat":
                            fat_idx = i
                        elif _txt == "Fib":
                            fiber_idx = i
                        elif _txt == "Pro":
                            protein_idx = i
                        elif _txt == "Carb":
                            carb_idx = i
                    if (
                        name_idx is None
                        or serv_idx is None
                        or fat_idx is None
                        or fiber_idx is None
                        or protein_idx is None
                        or carb_idx is None
                    ):
                        continue
                    body = desktop.find("tbody")
                    body_rows = body.find_all("tr")
                    for rest_row in body_rows:
                        tds = rest_row.find_all("td")
                        if len(tds) > 3:
                            writer.writerow(
                                [
                                    restaurant,
                                    tds[name_idx].text,
                                    tds[serv_idx].text,
                                    tds[fat_idx].text,
                                    tds[carb_idx].text,
                                    tds[fiber_idx].text,
                                    tds[protein_idx].text,
                                ]
                            )
                except Exception as e:
                    print(e)


def convert_string_fraction(frac):
    num, den = frac.split("/")
    return float(num) / float(den)


def split_serving_info(row):
    item = row["serving"]
    if isinstance(item, float):
        if math.isnan(item):
            return "each", 1, None
        return "oz", item, None
    if isinstance(item, str):
        val = item.strip().lower()
        if "topping" in val:
            return "each", val.split("topping")[0], "serving size is for a topping"
        if "serv" in val:
            return "each", val.split("serv")[0], None
        if "pckt" in val:
            return "each", val.split("pckt")[0], "each serving size refers to packet"
        if "packet" in val:
            return "each", val.split("packet")[0], "each serving size refers to packet"
        if "pint" in val:
            return "cup", 2 * val.split("pint")[0], None
        if "quart" in val:
            return "cup", 4 * val.split("quart")[0], None
        if "spoon" in val:
            return "each", val.split("spoon")[0], "each serving size refers to spoon"
        if "slice" in val:
            return "each", val.split("slice")[0], "each serving size refers to slice"
        if "roll" in val:
            return "each", val.split("roll")[0], "each serving size refers to roll"
        if "piece" in val:
            return "each", val.split("piece")[0], "each serving size refers to piece"
        if "unit" in val:
            return "each", val.split("unit")[0], "each serving size refers to unit"
        if "cone" in val:
            return "each", val.split("cone")[0], "each serving size refers to cone"
        if "wedge" in val:
            return "each", val.split("wedge")[0], "each serving size refers to wedge"
        if "bowl" in val:
            return "each", val.split("bowl")[0], "each serving size refers to bowl"
        if "bagel" in val:
            return "each", val.split("bagel")[0], "each serving size refers to bagel"
        if "egg" in val:
            return "each", val.split("egg")[0], "each serving size refers to egg"
        if "cont" in val:
            return "each", val.split("cont")[0], "each serving size refers to container"
        if "pouch" in val:
            return "each", val.split("pouch")[0], "each serving size refers to pouch"
        if "box" in val:
            return "each", val.split("box")[0], "each serving size refers to box"
        if "taco" in val:
            return "each", val.split("taco")[0], "each serving size refers to taco"
        if "bottle" in val:
            return "each", val.split("bottle")[0], "each serving size refers to bottle"
        if "can" in val:
            return "each", val.split("can")[0], "each serving size refers to can"
        if "tube" in val:
            return "each", val.split("tube")[0], "each serving size refers to tube"
        if "bag" in val:
            return "each", val.split("bag")[0], "each serving size refers to bag"
        if "ear" in val:
            return "each", val.split("ear")[0], "each serving size refers to ear"
        if "bite" in val:
            return "each", val.split("bite")[0], "each serving size refers to bite"
        if "bx" in val:
            return "each", val.split("bx")[0], "each serving size refers to box"
        if "link" in val:
            return "each", val.split("link")[0], "each serving size refers to link"
        if "rib" in val:
            return "each", val.split("rib")[0], "each serving size refers to rib"
        if "8 inch" in val:
            return "each", 1, "each serving size refers to a whole pizza"
        if "rosette" in val:
            return (
                "each",
                val.split("rosette")[0],
                "each serving size refers to rosette",
            )
        if "of pizza" in val:
            _val = val.split("of pizza")[0]
            try:
                return (
                    "each",
                    convert_string_fraction(_val),
                    "each serving size refers to a portion",
                )
            except ValueError:
                return "blah", 0, None
        if "tender" in val:
            return "each", val.split("tender")[0], "each serving size refers to tender"
        if "order" in val:
            return "each", val.split("order")[0], "each serving size refers to order"
        if "pak" in val:
            return "each", val.split("pak")[0], "each serving size refers to package"
        if "package" in val:
            return (
                "each",
                val.split("package")[0],
                "each serving size refers to package",
            )
        if "bun" in val:
            return "each", val.split("bun")[0], "each serving size refers to bun"
        if "shell" in val:
            return "each", val.split("shell")[0], "each serving size refers to shell"
        if "strip" in val:
            return "each", val.split("strip")[0], "each serving size refers to strip"
        if "salad" in val:
            return "each", val.split("salad")[0], "each serving size refers to salad"
        if "shot" in val:
            return "each", val.split("shot")[0], "each serving size refers to shot"
        if "bag" in val:
            return "each", val.split("bag")[0], "each serving size refers to bag"
        if "cookie" in val:
            return "each", val.split("cookie")[0], "each serving size refers to cookie"
        if "cooke" in val:
            return "each", val.split("cooke")[0], "each serving size refers to cookie"
        if "stix" in val:
            return "each", val.split("stix")[0], "each serving size refers to stix"
        if (
            "lg" == val
            or "reg" == val
            or "regular" == val
            or "med" == val
            or "medium" == val
            or "sm" == val
            or "small" == val
            or "average" == val
            or "individual" == val
            or "ind." == val
            or "whole" == val
        ):
            return "each", 1, None
        if "ring" in val:
            return "each", val.split("ring")[0], "each serving size refers to ring"
        if "item" in val:
            return "each", val.split("item")[0], "each serving size refers to item"
        if "cakes" in val:
            return "each", val.split("cakes")[0], "each serving size refers to cake"
        if "thin" in val:
            return "each", val.split("thin")[0], "each serving size refers to thin"
        if "pan" in val:
            return "each", val.split("pan")[0], "each serving size refers to pan"
        if "combo" in val:
            return "each", val.split("combo")[0], "each serving size refers to combo"
        if "scoop" in val:
            return "each", val.split("scoop")[0], "each serving size refers to scoop"
        if "meal" in val:
            return "each", val.split("meal")[0], "each serving size refers to meal"
        if "setup" in val:
            return "each", val.split("setup")[0], "each serving size refers to setup"
        if "pkg" in val:
            return "each", val.split("pkg")[0], "each serving size refers to package"
        if "tong" in val:
            return "each", val.split("tong")[0], "each serving size refers to tong"
        if "base" in val:
            return "each", val.split("base")[0], "each serving size refers to base"
        if "pie" in val:
            return "each", val.split("pie")[0], "each serving size refers to pie"
        if "per wing" in val:
            return "each", val.split("per wing")[0], "each serving size refers to wing"
        if "bskt" in val:
            return "each", val.split("bskt")[0], "each serving size refers to basket"
        if "platter" in val:
            return (
                "each",
                float(val.split("platter")[0]),
                "each serving size refers to platter",
            )
        if val[-4:] == "slab":
            return (
                "each",
                float(val.split("slab")[0]),
                "each serving size refers to slab",
            )
        if "portion" in val:
            _val = val.split("portion")[0]
            if "child" in _val.lower():
                return "each", 1, "each serving size refers to a child portion"
            try:
                return (
                    "each",
                    float(val.split("portion")[0]),
                    "each serving size refers to portion",
                )
            except ValueError:
                return "blah", 0, None
        if "fritter" in val:
            return (
                "each",
                float(val.split("fritter")[0]),
                "each serving size refers to fritter",
            )
        if val == "g":
            return "each", 1, "serving size is for a whole order"
        if val[-1] == "g":
            _val = val[:-1]
            try:
                return "gm", float(val[:-1]), None
            except ValueError:
                return "blah", 0, None
        if "fl. oz" in val:
            return "fl oz", val.split("fl. oz")[0], None
        if "fl.oz" in val:
            return "fl oz", val.split("fl.oz")[0], None
        if "fl oz" in val:
            return "fl oz", val.split("fl oz")[0], None
        if "floz" in val:
            return "fl oz", val.split("floz")[0], None
        if val[-2:] == "oz":
            _val = val[:-2]
            try:
                return "oz", float(val[:-2]), None
            except ValueError:
                return "blah", 0, None
        if val[-3:] == "oz.":
            _val = val[:-3]
            try:
                return "oz", float(val[:-3]), None
            except ValueError:
                return "blah", 0, None
        if val[-2:] == "ml":
            _val = val[:-1]
            try:
                return "ml", float(val[:-2]), None
            except ValueError:
                return "blah", 0, None
        if "(ml)" in val:
            try:
                return "ml", float(val.split("(ml)")[0]), None
            except ValueError:
                return "blah", 0, None
        if "per salad" in val:
            return "each", 1, "serving size refers to a salad"
        if " oz " in val:
            _val = val.split(" oz ")[0]
            try:
                return "oz", float(val.split(" oz ")[0]), None
            except ValueError:
                return "blah", 0, None
        if val[-2:] == "pc":
            return (
                "each",
                float(val.split("pc")[0]),
                "each serving size refers to piece",
            )
        if val[-3:] == "pcs":
            return (
                "each",
                float(val.split("pc")[0]),
                "each serving size refers to piece",
            )

        if val[-3:] == " ea":
            return "each", val.split(" ea")[0], None
        if val[-2:] == "sl":
            return "each", val.split("sl")[0], "each serving size refers to slice"
        if val[-4:] == " ea.":
            return "each", val.split(" ea")[0], None
        if val[-3:] == "ea.":
            return "each", val.split("ea")[0], None
        if val[-2:] == "ea":
            return "each", val.split("ea")[0], None
        if val[-4:] == " ct.":
            return "each", val.split(" ct")[0], None
        if val[-4:] == " pc.":
            return "each", val.split(" pc")[0], None
        if val[-4:] == " cup":
            _val = val.split(" cup")[0]
            try:
                return "cup", float(_val), None
            except ValueError:
                try:
                    return "cup", convert_string_fraction(_val), None
                except ValueError:
                    return "blah", 1234, None
        if val[-4:] == " tsp":
            _val = val.split("tsp")[0]
            try:
                return "tsp", float(_val), None
            except ValueError:
                try:
                    return "tsp", convert_string_fraction(_val), None
                except (ValueError, TypeError):
                    return "blah", 0, None
        if val[-5:] == " tbsp":
            _val = val.split(" tbsp")[0]
            try:
                return "tbsp", float(_val), None
            except ValueError:
                try:
                    return "tbsp", convert_string_fraction(_val), None
                except (ValueError, TypeError):
                    return "blah", 0, None
        if val[-5:] == "tbsp.":
            _val = val.split("tbsp")[0]
            try:
                return "tbsp", float(_val), None
            except ValueError:
                try:
                    return "tbsp", convert_string_fraction(_val), None
                except (ValueError, TypeError):
                    return "blah", 0, None
        if "tbsp" in val:
            _val = val.split("tbsp")[0]
            try:
                return "tbsp", float(_val), None
            except ValueError:
                try:
                    return "tbsp", convert_string_fraction(_val), None
                except (ValueError, TypeError):
                    return "blah", 0, None
        if val[-4:] == "each":
            _val = val.split("each")[0]
            try:
                return "each", float(_val), None
            except ValueError:
                try:
                    return "each", convert_string_fraction(_val), None
                except (ValueError, TypeError):
                    return "blah", 0, None
        if val[-2:] == "lb":
            _val = val.split("lb")[0]
            try:
                return "lb", float(_val), None
            except ValueError:
                try:
                    return "lb", convert_string_fraction(_val), None
                except ValueError:
                    return "blah", 0, None
        if val[-3:] == "lb.":
            _val = val.split("lb")[0]
            try:
                return "lb", float(_val), None
            except ValueError:
                return "blah", convert_string_fraction(_val), None
        if row["restaurant"] == "Godfather's Pizza":
            try:
                convert_string_fraction(val)
                return "each", 1, "serving size refers to each portion of the whole"
            except ValueError:
                return "blah", 0, None
        if row["restaurant"] == "Marco's Pizza":
            if "pizza" in val:
                if "Add Topping " in row["name"]:
                    return "each", 1, "serving size refers to a topping"
                return "each", 1, "serving size refers to a pizza"
    return "blah", 999, None
    # if isinstance(item, str):
    #     if isinstance(item[-1], str) and item[-1].strip() == "g":
    #         try:
    #             float(item[:-1])
    #         except ValueError:
    #             print(item)


def clean_data():
    df = pd.read_csv("./restaurant_foods.csv")
    serving_df = df.apply(split_serving_info, axis=1, result_type="expand")
    df["serving_size"] = serving_df[1]
    df["serving_unit"] = serving_df[0]
    df["notes"] = serving_df[2]
    # df.dropna(inplace=True, axis=1, subset=["serving_unit"])
    return df


if __name__ == "__main__":
    # get_data()
    df = clean_data()
    df.to_csv("blah.csv", index=False)
