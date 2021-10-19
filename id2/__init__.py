# -*- coding: utf-8 -*-

"""Detect and directly open DOIs, ISBNs, OrcIDs, crypto-addresses, geo-coordinates, and more in your web-browser. Examples:

- Unicode:  "U+1F194"
- UnixTime: "1606324253"
- Location: "8FWH4HX8+QR"
- DOI:      "10.1109/FDL.2018.8524068"
- OrcID:    "0000-0002-0006-7761"
- BitCoin:  "3FZbgi29cpjq2GjdwV8eyHuJJnkLtktZc5"

There is no trigger required. For a full list, see https://id2.dev"""

import re
import os
import json

from albert import UrlAction, Item, iconLookup

__title__ = "ID2 Identifier Resolver"
__version__ = "0.4.4"
__authors__ = ["Emanuel Regnath"]


# globals
iconPath = iconLookup(["www", "web-browser"])
id2data = {}



def guessId(token, idclass=None):
    """Test if "token" matches the regex of any identifier and return all found types. If idclass is given, only test those."""
    token = token.strip()
    types = []
    for key, entry in id2data.items():
        if idclass and idclass != key[0]: continue
        #sys.stderr.write("\n{}: {}".format(key, len(token)))
        if len(token) in entry["lens"]:
            regex = entry["re"]
            match = re.match(r'^'+regex+r'$', token)
            if match:
                entry["part"]=match.group(1)
                types.append(entry)
    return types


def parseIdentifierLengthsOnce():
    """parse "len" key string and assign a list of integers to speed up execution"""
    lens = []
    for key, entry in id2data.items():
        parts = entry['len'].split(",")
        for part in parts:
            nums = part.split("-")
            imin = int(nums[0])
            if(len(nums) == 2):
                if(nums[1] == ""): nums[1] = "40"
                imax = int(nums[1])
                lens = list(range(imin, imax+1))
            else:
                lens.append(imin)

        id2data[key]['lens'] = lens


# Implements API: executed on every key input
def handleQuery(query):
    token = query.string.strip()
    if len(token) < 5: return None

    items = []
    types = guessId(token)

    for el in types:
        items.append(Item(
            id = __title__,
            icon = iconPath,
            text = token,
            subtext = "Open "+el["desc"],
            actions = [UrlAction(text="Open in Browser.", url=el["url"]+el["part"])]
        ))

    return items



# Implements API: executed on load
def initialize():
    global iconPath
    global id2data

    # load ID regex entries
    id2Path = os.path.dirname(__file__)+"/id2data.json"
    with open(id2Path) as json_file:
        id2data = json.load(json_file)

    # compute lengths
    parseIdentifierLengthsOnce()

    if iconPath == "":
        iconPath=os.path.dirname(__file__)+"/web-browser.svg"
