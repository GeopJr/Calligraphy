# fonts_list.py
#
# Copyright 2023 Calligraphy Contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later
from pyfiglet import Figlet, FigletFont
from .env import DEVEL

FONTS_LIST = {
    "3D Diagonal": "3d_diagonal",
    "3D": "3-d",
    "4MAX": "4max",
    "5-line Oblique": "5lineoblique",
    "Acrobatic": "acrobatic",
    "Alligator": "alligator2",
    "Alligator Italic": "alligator",
    "Amc AAA 01": "amc_aaa01",
    "Arrows": "arrows",
    "Avatar": "avatar",
    "Banner 3D": "banner3-D",
    "Barbwire": "barbwire",
    "Bears": "bear",
    "Bell": "bell",
    "Big Chief": "bigchief",
    "Big Money": "big_money-nw",
    "Big": "big",
    "Block": "block",
    "Blocks": "blocks",
    "Blocky": "blocky",
    "Blood": "sblood",
    "Bloody": "bloody",
    "Bolger": "bolger",
    "Bright": "bright",
    "Calligraphy": "calgphy2",
    "Cards": "cards",
    "Chunky": "chunky",
    "CLB 6x10": "clb6x10",
    "Coin Stack": "coinstak",
    "Colossal": "colossal",
    "Cosmic": "cosmic",
    "Crawford": "crawford",
    "Crazy": "crazy",
    "Cricket": "cricket",
    "Cursive": "cursive",
    "Cyber Large": "cyberlarge",
    "Dancing Font": "dancing_font",
    "Def Leppard": "def_leppard",
    "Def Leppard": "defleppard",
    "Delta Corps Priest": "delta_corps_priest_1",
    "Demo": "demo_1__",
    "Diet Cola": "diet_cola",
    "Doh": "doh",
    "Dos Rebel": "dos_rebel",
    "Dot Matrix": "dotmatrix",
    "Dr Pepper": "drpepper",
    "Electronic": "electronic",
    "Elite": "elite",
    "Epic": "epic",
    "Fender": "fender",
    "Filter": "filter",
    "Flower Power": "flower_power",
    "Fraktur": "fraktur",
    "Fraktur": "fraktur",
    "Fun Faces": "fun_faces",
    "Fuzzy": "fuzzy",
    "Georgia 11": "georgia11",
    "Ghost": "ghost",
    "Goofy": "goofy",
    "Gothic": "gothic",
    "Graceful": "graceful",
    "Gradient": "gradient",
    "Graffiti": "graffiti",
    "Heart Left": "heart_left",
    "Heart Right": "heart_right",
    "Henry 3D": "henry_3d",
    "Hollywood": "hollywood",
    "Impossible": "impossible",
    "Invita": "invita",
    "Isometric": "isometric3",
    "Jazmine": "jazmine",
    "Jazmine": "jazmine",
    "Kban": "kban",
    "Keyboard": "keyboard",
    "Larry 3D": "larry3d",
    "Lean": "lean",
    "Letters": "letters",
    "Lil Devil": "lil_devil",
    "Marquee": "marquee",
    "Merlin": "merlin2",
    "N Script": "nscript",
    "Nancyj Fancy": "nancyj-fancy",
    "Nancyj": "nancyj",
    "Neko": "amc_neko",
    "NPN": "npn_____",
    "Ogre": "ogre",
    "OS": "os2",
    "Patorjk Hex": "patorjk-hex",
    "Pawp": "pawp",
    "Peaks": "peaks",
    "Poison": "poison",
    "Small Poison": "small_poison",
    "Puffy": "puffy",
    "Puffy": "puffy",
    "Puzzle": "puzzle",
    "Razor": "amc_razor2",
    "Relief": "relief",
    "Relief 2": "relief2",
    "Relief Italics": "slant_relief",
    "Rev": "rev",
    "Roman": "roman",
    "Rowancap": "rowancap",
    "Rozzo": "rozzo",
    "Script": "script",
    "Serifcap": "serifcap",
    "Shimrod": "shimrod",
    "Small": "small",
    "Smisome": "smisome1",
    "Space OP": "space_op",
    "Speed": "speed",
    "Stampate": "stampate",
    "Star Wars": "starwars",
    "Stellar": "stellar",
    "Tanja": "tanja",
    "The Edge": "the_edge",
    "Thin": "thin",
    "This": "this",
    "Ticks": "ticks",
    "Ticks Italic": "ticksslant",
    "Tiles": "tiles",
    "Tombstone": "tombstone",
    "Train": "train",
    "Tubular": "tubular",
    "Twisted": "twisted",
    "Universe": "univers",
    "USA Flag": "usaflag",
    "Varsity": "varsity",
    "Wet Letter": "wet_letter",
}

if DEVEL:
    print(f"DEBUG: All fonts {FigletFont.getFonts()}")
    multi_fonts = {}
    for key, value in FONTS_LIST.items():
        multi_fonts.setdefault(value, set()).add(key)
    dups = [key for key, values in multi_fonts.items() if len(values) > 1]
    if len(dups) > 0:
        print(f"WARNING: Following fonts are listed multiple times, {dups}")


def convert_to_fonts():
    inf = float("inf")
    for key in FONTS_LIST:
        FONTS_LIST[key] = Figlet(font=FONTS_LIST[key], width=inf)
