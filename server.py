import re
import sys
import copy

from pprint import pprint

import requests
from bs4 import BeautifulSoup



def line_cite(line, cite, css_class):
    return f"<p class='{css_class}' id='{cite}'>{line}</p>\n"

  
def extract_labels(filtered_statute, law_info):
    """Returns provisions, a list corresponding to the lines of content.
    Each element in the list is a tuple of four parts:
        1. A list of matching label types.
        2. the section number (the specific cite will be decided later)
        2. the text of the label itself ("1","2","A","B").
        3. The text of the line (or the rest of the line if there is a label).

    """
    provisions = []
    label_matches = []
    official_section = ""
    for (category, section, text) in filtered_statute:

        #     List of patterns of increasing depth.
        if category == "bill_heading":

            label_matches.append("bill_heading")

            official_section = section

            provisions.append((label_matches, section, "", text))

        elif category == "law_heading":

            label_matches.append("law_heading")

            official_section = section

            provisions.append((label_matches, official_section, "", text))

        elif category == "paragraph":

            label_text = re.match("\((.{1,5})\)(.*)", text)

            pattern_re = {
                "\(([a-z]{1,3})\).*": "lower",
                "\(([\d]{1,2})\).*": "arabic",
                "\(([A-Z]{1,3})\).*": "capital",
                "\((M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}))\).*": "roman",
                "\((m{0,4}(cm|cd|d?c{0,3})(xc|xl|l?x{0,3})(ix|iv|v?i{0,3}))\).*": "romanette",
            }

            # content_type_re = {}

            for key in pattern_re:

                # create dict going the other direction to use later.
                # content_type_re[pattern_re[key]] = key

                # if there's a match, add to label_matches list.
                if re.match(key, text):
                    label_matches.append(pattern_re[key])

            # Add labels and text to the list of provisions
            if label_text:

                provisions.append(
                    (
                        label_matches,
                        official_section,
                        label_text.group(1),
                        label_text.group(2),
                    )
                )

            if len(label_matches) == 0:
                # print(text)
                provisions.append((label_matches, official_section, "", text))
                no_label = True
                label_matches.append("none")

        label_matches = []

    return provisions


def increment_status(match, status):
    status[index(match)] += 1
    return status


def get_key(val, my_dict):
    """small helper function to return key for any value in a dictionary."""

    for key, value in my_dict.items():
        if val == value:
            return key
    raise KeyError


def reset_status(reset_above, status, outline_depth):
    """When there is a heading or the indentation level decreases,
    set the status to a lower number."""

    status['depth'] = reset_above
    for i in range(reset_above + 1, 7):
        # print(f"i:{i}")
        status[get_key(i, outline_depth)] = 0
    return status


def depth_permission(depth, outline_depth):
    """This function determines how the permissible labels change based on
    the current depth in the outline.
     So maybe call this something like increment permission by depth?"""
    if depth == 0 and outline_depth == 2:
        return 1
    elif outline_depth <= depth + 1:
        return 1
    else:
        return 0


def get_labels(label_type):
    """
    Takes a string label_type and returns a list of labels.

    The `lower2` label allows lower to be re-used in status, which
    is a dictionary and therefore must have unique keys. Note that for
    and repeated use of labels more entries will need to be added to this
    dictionary (so arabic2, capital2, etc).
    """

    # LOWER = ["0","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","aa","bb","cc","dd","ee","ff","gg","hh","ii","jj","kk","ll","mm","nn","oo","pp","qq","rr","ss","tt","uu","vv","ww","xx","yy","zz"]
    LOWER = [
        "0",
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
        "aa",
        "ab",
        "ac",
        "ad",
        "ae",
        "af",
        "ag",
        "ah",
        "ai",
        "aj",
        "ak",
        "al",
        "am",
        "an",
        "ao",
        "ap",
        "aq",
        "ar",
        "as",
        "at",
        "au",
        "av",
        "aw",
        "ax",
        "ay",
        "az",
    ]

    ARABIC = ["0"]
    ARABIC.extend([str(i + 1) for i in range(500)])

    CAPITAL = [
        "0",
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
        "Z",
        "AA",
        "BB",
        "CC",
        "DD",
        "EE",
        "FF",
        "GG",
        "HH",
        "II",
        "JJ",
        "KK",
        "LL",
        "MM",
        "NN",
        "OO",
        "PP",
        "QQ",
        "RR",
        "SS",
        "TT",
        "UU",
        "VV",
        "WW",
        "XX",
        "YY",
        "ZZ",
    ]

    ROMANETTE = [
        "0",
        "i",
        "ii",
        "iii",
        "iv",
        "v",
        "vi",
        "vii",
        "viii",
        "ix",
        "x",
        "xi",
        "xii",
        "xiii",
        "xiv",
        "xv",
        "xvi",
        "xvii",
        "xviii",
        "xix",
        "xx",
        "xxi",
        "xxii",
        "xxiii",
        "xxiv",
        "xxv",
        "xxvi",
        "xxvii",
        "xxviii",
        "xxix",
        "xxx",
        "xxxi",
        "xxxii",
        "xxxiii",
        "xxxiv",
        "xxxv",
        "xxxvi",
        "xxxvii",
        "xxxviii",
        "xxxix",
        "xl",
        "xli",
        "xlii",
        "xliii",
        "xliv",
        "xlv",
        "xlvi",
        "xlvii",
        "xlviii",
        "xlix",
        "l",
        "li",
        "lii",
        "liii",
        "liv",
        "lv",
        "lvi",
        "lvii",
        "lviii",
        "lix",
        "lx",
        "lxi",
        "lxii",
        "lxiii",
        "lxiv",
        "lxv",
        "lxvi",
        "lxvii",
        "lxviii",
        "lxix",
        "lxx",
        "lxxi",
        "lxxii",
        "lxxiii",
        "lxxiv",
        "lxxv",
        "lxxvi",
        "lxxvii",
        "lxxviii",
        "lxxix",
        "lxxx",
        "lxxxi",
        "lxxxii",
        "lxxxiii",
        "lxxxiv",
        "lxxxv",
        "lxxxvi",
        "lxxxvii",
        "lxxxviii",
        "lxxxix",
        "xc",
        "xci",
        "xcii",
        "xciii",
        "xciv",
        "xcv",
        "xcvi",
        "xcvii",
        "xcviii",
        "xcix",
        "c",
        "ci",
        "cii",
        "ciii",
        "civ",
        "cv",
        "cvi",
        "cvii",
        "cviii",
        "cix",
        "cx",
        "cxi",
        "cxii",
        "cxiii",
        "cxiv",
        "cxv",
        "cxvi",
        "cxvii",
        "cxviii",
        "cxix",
        "cxx",
        "cxxi",
        "cxxii",
        "cxxiii",
        "cxxiv",
        "cxxv",
        "cxxvi",
        "cxxvii",
        "cxxviii",
        "cxxix",
        "cxxx",
        "cxxxi",
        "cxxxii",
        "cxxxiii",
        "cxxxiv",
        "cxxxv",
        "cxxxvi",
        "cxxxvii",
        "cxxxviii",
        "cxxxix",
        "cxl",
        "cxli",
        "cxlii",
        "cxliii",
        "cxliv",
        "cxlv",
        "cxlvi",
        "cxlvii",
        "cxlviii",
        "cxlix",
        "cl",
        "cli",
        "clii",
        "cliii",
        "cliv",
        "clv",
        "clvi",
        "clvii",
        "clviii",
        "clix",
        "clx",
        "clxi",
        "clxii",
        "clxiii",
        "clxiv",
        "clxv",
        "clxvi",
        "clxvii",
        "clxviii",
        "clxix",
        "clxx",
        "clxxi",
        "clxxii",
        "clxxiii",
        "clxxiv",
        "clxxv",
        "clxxvi",
        "clxxvii",
        "clxxviii",
        "clxxix",
        "clxxx",
        "clxxxi",
        "clxxxii",
        "clxxxiii",
        "clxxxiv",
        "clxxxv",
        "clxxxvi",
        "clxxxvii",
        "clxxxviii",
        "clxxxix",
        "cxc",
        "cxci",
        "cxcii",
        "cxciii",
        "cxciv",
        "cxcv",
        "cxcvi",
        "cxcvii",
        "cxcviii",
        "cxcix",
        "cc",
        "cci",
        "ccii",
        "cciii",
        "cciv",
        "ccv",
        "ccvi",
        "ccvii",
        "ccviii",
        "ccix",
        "ccx",
        "ccxi",
        "ccxii",
        "ccxiii",
        "ccxiv",
        "ccxv",
        "ccxvi",
        "ccxvii",
        "ccxviii",
        "ccxix",
        "ccxx",
        "ccxxi",
        "ccxxii",
        "ccxxiii",
        "ccxxiv",
        "ccxxv",
        "ccxxvi",
        "ccxxvii",
        "ccxxviii",
        "ccxxix",
        "ccxxx",
        "ccxxxi",
        "ccxxxii",
        "ccxxxiii",
        "ccxxxiv",
        "ccxxxv",
        "ccxxxvi",
        "ccxxxvii",
        "ccxxxviii",
        "ccxxxix",
        "ccxl",
        "ccxli",
        "ccxlii",
        "ccxliii",
        "ccxliv",
        "ccxlv",
        "ccxlvi",
        "ccxlvii",
        "ccxlviii",
        "ccxlix",
        "ccl",
        "ccli",
        "cclii",
        "ccliii",
        "ccliv",
        "cclv",
        "cclvi",
        "cclvii",
        "cclviii",
        "cclix",
        "cclx",
        "cclxi",
        "cclxii",
        "cclxiii",
        "cclxiv",
        "cclxv",
        "cclxvi",
        "cclxvii",
        "cclxviii",
        "cclxix",
        "cclxx",
        "cclxxi",
        "cclxxii",
        "cclxxiii",
        "cclxxiv",
        "cclxxv",
        "cclxxvi",
        "cclxxvii",
        "cclxxviii",
        "cclxxix",
        "cclxxx",
        "cclxxxi",
        "cclxxxii",
        "cclxxxiii",
        "cclxxxiv",
        "cclxxxv",
        "cclxxxvi",
        "cclxxxvii",
        "cclxxxviii",
        "cclxxxix",
        "ccxc",
        "ccxci",
        "ccxcii",
        "ccxciii",
        "ccxciv",
        "ccxcv",
        "ccxcvi",
        "ccxcvii",
        "ccxcviii",
        "ccxcix",
        "ccc",
        "ccci",
        "cccii",
        "ccciii",
        "ccciv",
        "cccv",
        "cccvi",
        "cccvii",
        "cccviii",
        "cccix",
        "cccx",
        "cccxi",
        "cccxii",
        "cccxiii",
        "cccxiv",
        "cccxv",
        "cccxvi",
        "cccxvii",
        "cccxviii",
        "cccxix",
        "cccxx",
        "cccxxi",
        "cccxxii",
        "cccxxiii",
        "cccxxiv",
        "cccxxv",
        "cccxxvi",
        "cccxxvii",
        "cccxxviii",
        "cccxxix",
        "cccxxx",
        "cccxxxi",
        "cccxxxii",
        "cccxxxiii",
        "cccxxxiv",
        "cccxxxv",
        "cccxxxvi",
        "cccxxxvii",
        "cccxxxviii",
        "cccxxxix",
        "cccxl",
        "cccxli",
        "cccxlii",
        "cccxliii",
        "cccxliv",
        "cccxlv",
        "cccxlvi",
        "cccxlvii",
        "cccxlviii",
        "cccxlix",
        "cccl",
        "cccli",
        "ccclii",
        "cccliii",
        "cccliv",
        "ccclv",
        "ccclvi",
        "ccclvii",
        "ccclviii",
        "ccclix",
        "ccclx",
        "ccclxi",
        "ccclxii",
        "ccclxiii",
        "ccclxiv",
        "ccclxv",
        "ccclxvi",
        "ccclxvii",
        "ccclxviii",
        "ccclxix",
        "ccclxx",
        "ccclxxi",
        "ccclxxii",
        "ccclxxiii",
        "ccclxxiv",
        "ccclxxv",
        "ccclxxvi",
        "ccclxxvii",
        "ccclxxviii",
        "ccclxxix",
        "ccclxxx",
        "ccclxxxi",
        "ccclxxxii",
        "ccclxxxiii",
        "ccclxxxiv",
        "ccclxxxv",
        "ccclxxxvi",
        "ccclxxxvii",
        "ccclxxxviii",
        "ccclxxxix",
        "cccxc",
        "cccxci",
        "cccxcii",
        "cccxciii",
        "cccxciv",
        "cccxcv",
        "cccxcvi",
        "cccxcvii",
        "cccxcviii",
        "cccxcix",
        "cd",
        "cdi",
        "cdii",
        "cdiii",
        "cdiv",
        "cdv",
        "cdvi",
        "cdvii",
        "cdviii",
        "cdix",
        "cdx",
        "cdxi",
        "cdxii",
        "cdxiii",
        "cdxiv",
        "cdxv",
        "cdxvi",
        "cdxvii",
        "cdxviii",
        "cdxix",
        "cdxx",
        "cdxxi",
        "cdxxii",
        "cdxxiii",
        "cdxxiv",
        "cdxxv",
        "cdxxvi",
        "cdxxvii",
        "cdxxviii",
        "cdxxix",
        "cdxxx",
        "cdxxxi",
        "cdxxxii",
        "cdxxxiii",
        "cdxxxiv",
        "cdxxxv",
        "cdxxxvi",
        "cdxxxvii",
        "cdxxxviii",
        "cdxxxix",
        "cdxl",
        "cdxli",
        "cdxlii",
        "cdxliii",
        "cdxliv",
        "cdxlv",
        "cdxlvi",
        "cdxlvii",
        "cdxlviii",
        "cdxlix",
        "cdl",
        "cdli",
        "cdlii",
        "cdliii",
        "cdliv",
        "cdlv",
        "cdlvi",
        "cdlvii",
        "cdlviii",
        "cdlix",
        "cdlx",
        "cdlxi",
        "cdlxii",
        "cdlxiii",
        "cdlxiv",
        "cdlxv",
        "cdlxvi",
        "cdlxvii",
        "cdlxviii",
        "cdlxix",
        "cdlxx",
        "cdlxxi",
        "cdlxxii",
        "cdlxxiii",
        "cdlxxiv",
        "cdlxxv",
        "cdlxxvi",
        "cdlxxvii",
        "cdlxxviii",
        "cdlxxix",
        "cdlxxx",
        "cdlxxxi",
        "cdlxxxii",
        "cdlxxxiii",
        "cdlxxxiv",
        "cdlxxxv",
        "cdlxxxvi",
        "cdlxxxvii",
        "cdlxxxviii",
        "cdlxxxix",
        "cdxc",
        "cdxci",
        "cdxcii",
        "cdxciii",
        "cdxciv",
        "cdxcv",
        "cdxcvi",
        "cdxcvii",
        "cdxcviii",
        "cdxcix",
        "d",
    ]

    ROMAN = [
        "0",
        "I",
        "II",
        "III",
        "IV",
        "V",
        "VI",
        "VII",
        "VIII",
        "IX",
        "X",
        "XI",
        "XII",
        "XIII",
        "XIV",
        "XV",
        "XVI",
        "XVII",
        "XVIII",
        "XIX",
        "XX",
        "XXI",
        "XXII",
        "XXIII",
        "XXIV",
        "XXV",
        "XXVI",
        "XXVII",
        "XXVIII",
        "XXIX",
        "XXX",
        "XXXI",
        "XXXII",
        "XXXIII",
        "XXXIV",
        "XXXV",
        "XXXVI",
        "XXXVII",
        "XXXVIII",
        "XXXIX",
        "XL",
        "XLI",
        "XLII",
        "XLIII",
        "XLIV",
        "XLV",
        "XLVI",
        "XLVII",
        "XLVIII",
        "XLIX",
        "L",
        "LI",
        "LII",
        "LIII",
        "LIV",
        "LV",
        "LVI",
        "LVII",
        "LVIII",
        "LIX",
        "LX",
        "LXI",
        "LXII",
        "LXIII",
        "LXIV",
        "LXV",
        "LXVI",
        "LXVII",
        "LXVIII",
        "LXIX",
        "LXX",
        "LXXI",
        "LXXII",
        "LXXIII",
        "LXXIV",
        "LXXV",
        "LXXVI",
        "LXXVII",
        "LXXVIII",
        "LXXIX",
        "LXXX",
        "LXXXI",
        "LXXXII",
        "LXXXIII",
        "LXXXIV",
        "LXXXV",
        "LXXXVI",
        "LXXXVII",
        "LXXXVIII",
        "LXXXIX",
        "XC",
        "XCI",
        "XCII",
        "XCIII",
        "XCIV",
        "XCV",
        "XCVI",
        "XCVII",
        "XCVIII",
        "XCIX",
        "C",
        "CI",
        "CII",
        "CIII",
        "CIV",
        "CV",
        "CVI",
        "CVII",
        "CVIII",
        "CIX",
        "CX",
        "CXI",
        "CXII",
        "CXIII",
        "CXIV",
        "CXV",
        "CXVI",
        "CXVII",
        "CXVIII",
        "CXIX",
        "CXX",
        "CXXI",
        "CXXII",
        "CXXIII",
        "CXXIV",
        "CXXV",
        "CXXVI",
        "CXXVII",
        "CXXVIII",
        "CXXIX",
        "CXXX",
        "CXXXI",
        "CXXXII",
        "CXXXIII",
        "CXXXIV",
        "CXXXV",
        "CXXXVI",
        "CXXXVII",
        "CXXXVIII",
        "CXXXIX",
        "CXL",
        "CXLI",
        "CXLII",
        "CXLIII",
        "CXLIV",
        "CXLV",
        "CXLVI",
        "CXLVII",
        "CXLVIII",
        "CXLIX",
        "CL",
        "CLI",
        "CLII",
        "CLIII",
        "CLIV",
        "CLV",
        "CLVI",
        "CLVII",
        "CLVIII",
        "CLIX",
        "CLX",
        "CLXI",
        "CLXII",
        "CLXIII",
        "CLXIV",
        "CLXV",
        "CLXVI",
        "CLXVII",
        "CLXVIII",
        "CLXIX",
        "CLXX",
        "CLXXI",
        "CLXXII",
        "CLXXIII",
        "CLXXIV",
        "CLXXV",
        "CLXXVI",
        "CLXXVII",
        "CLXXVIII",
        "CLXXIX",
        "CLXXX",
        "CLXXXI",
        "CLXXXII",
        "CLXXXIII",
        "CLXXXIV",
        "CLXXXV",
        "CLXXXVI",
        "CLXXXVII",
        "CLXXXVIII",
        "CLXXXIX",
        "CXC",
        "CXCI",
        "CXCII",
        "CXCIII",
        "CXCIV",
        "CXCV",
        "CXCVI",
        "CXCVII",
        "CXCVIII",
        "CXCIX",
        "CC",
        "CCI",
        "CCII",
        "CCIII",
        "CCIV",
        "CCV",
        "CCVI",
        "CCVII",
        "CCVIII",
        "CCIX",
        "CCX",
        "CCXI",
        "CCXII",
        "CCXIII",
        "CCXIV",
        "CCXV",
        "CCXVI",
        "CCXVII",
        "CCXVIII",
        "CCXIX",
        "CCXX",
        "CCXXI",
        "CCXXII",
        "CCXXIII",
        "CCXXIV",
        "CCXXV",
        "CCXXVI",
        "CCXXVII",
        "CCXXVIII",
        "CCXXIX",
        "CCXXX",
        "CCXXXI",
        "CCXXXII",
        "CCXXXIII",
        "CCXXXIV",
        "CCXXXV",
        "CCXXXVI",
        "CCXXXVII",
        "CCXXXVIII",
        "CCXXXIX",
        "CCXL",
        "CCXLI",
        "CCXLII",
        "CCXLIII",
        "CCXLIV",
        "CCXLV",
        "CCXLVI",
        "CCXLVII",
        "CCXLVIII",
        "CCXLIX",
        "CCL",
        "CCLI",
        "CCLII",
        "CCLIII",
        "CCLIV",
        "CCLV",
        "CCLVI",
        "CCLVII",
        "CCLVIII",
        "CCLIX",
        "CCLX",
        "CCLXI",
        "CCLXII",
        "CCLXIII",
        "CCLXIV",
        "CCLXV",
        "CCLXVI",
        "CCLXVII",
        "CCLXVIII",
        "CCLXIX",
        "CCLXX",
        "CCLXXI",
        "CCLXXII",
        "CCLXXIII",
        "CCLXXIV",
        "CCLXXV",
        "CCLXXVI",
        "CCLXXVII",
        "CCLXXVIII",
        "CCLXXIX",
        "CCLXXX",
        "CCLXXXI",
        "CCLXXXII",
        "CCLXXXIII",
        "CCLXXXIV",
        "CCLXXXV",
        "CCLXXXVI",
        "CCLXXXVII",
        "CCLXXXVIII",
        "CCLXXXIX",
        "CCXC",
        "CCXCI",
        "CCXCII",
        "CCXCIII",
        "CCXCIV",
        "CCXCV",
        "CCXCVI",
        "CCXCVII",
        "CCXCVIII",
        "CCXCIX",
        "CCC",
        "CCCI",
        "CCCII",
        "CCCIII",
        "CCCIV",
        "CCCV",
        "CCCVI",
        "CCCVII",
        "CCCVIII",
        "CCCIX",
        "CCCX",
        "CCCXI",
        "CCCXII",
        "CCCXIII",
        "CCCXIV",
        "CCCXV",
        "CCCXVI",
        "CCCXVII",
        "CCCXVIII",
        "CCCXIX",
        "CCCXX",
        "CCCXXI",
        "CCCXXII",
        "CCCXXIII",
        "CCCXXIV",
        "CCCXXV",
        "CCCXXVI",
        "CCCXXVII",
        "CCCXXVIII",
        "CCCXXIX",
        "CCCXXX",
        "CCCXXXI",
        "CCCXXXII",
        "CCCXXXIII",
        "CCCXXXIV",
        "CCCXXXV",
        "CCCXXXVI",
        "CCCXXXVII",
        "CCCXXXVIII",
        "CCCXXXIX",
        "CCCXL",
        "CCCXLI",
        "CCCXLII",
        "CCCXLIII",
        "CCCXLIV",
        "CCCXLV",
        "CCCXLVI",
        "CCCXLVII",
        "CCCXLVIII",
        "CCCXLIX",
        "CCCL",
        "CCCLI",
        "CCCLII",
        "CCCLIII",
        "CCCLIV",
        "CCCLV",
        "CCCLVI",
        "CCCLVII",
        "CCCLVIII",
        "CCCLIX",
        "CCCLX",
        "CCCLXI",
        "CCCLXII",
        "CCCLXIII",
        "CCCLXIV",
        "CCCLXV",
        "CCCLXVI",
        "CCCLXVII",
        "CCCLXVIII",
        "CCCLXIX",
        "CCCLXX",
        "CCCLXXI",
        "CCCLXXII",
        "CCCLXXIII",
        "CCCLXXIV",
        "CCCLXXV",
        "CCCLXXVI",
        "CCCLXXVII",
        "CCCLXXVIII",
        "CCCLXXIX",
        "CCCLXXX",
        "CCCLXXXI",
        "CCCLXXXII",
        "CCCLXXXIII",
        "CCCLXXXIV",
        "CCCLXXXV",
        "CCCLXXXVI",
        "CCCLXXXVII",
        "CCCLXXXVIII",
        "CCCLXXXIX",
        "CCCXC",
        "CCCXCI",
        "CCCXCII",
        "CCCXCIII",
        "CCCXCIV",
        "CCCXCV",
        "CCCXCVI",
        "CCCXCVII",
        "CCCXCVIII",
        "CCCXCIX",
        "CD",
        "CDI",
        "CDII",
        "CDIII",
        "CDIV",
        "CDV",
        "CDVI",
        "CDVII",
        "CDVIII",
        "CDIX",
        "CDX",
        "CDXI",
        "CDXII",
        "CDXIII",
        "CDXIV",
        "CDXV",
        "CDXVI",
        "CDXVII",
        "CDXVIII",
        "CDXIX",
        "CDXX",
        "CDXXI",
        "CDXXII",
        "CDXXIII",
        "CDXXIV",
        "CDXXV",
        "CDXXVI",
        "CDXXVII",
        "CDXXVIII",
        "CDXXIX",
        "CDXXX",
        "CDXXXI",
        "CDXXXII",
        "CDXXXIII",
        "CDXXXIV",
        "CDXXXV",
        "CDXXXVI",
        "CDXXXVII",
        "CDXXXVIII",
        "CDXXXIX",
        "CDXL",
        "CDXLI",
        "CDXLII",
        "CDXLIII",
        "CDXLIV",
        "CDXLV",
        "CDXLVI",
        "CDXLVII",
        "CDXLVIII",
        "CDXLIX",
        "CDL",
        "CDLI",
        "CDLII",
        "CDLIII",
        "CDLIV",
        "CDLV",
        "CDLVI",
        "CDLVII",
        "CDLVIII",
        "CDLIX",
        "CDLX",
        "CDLXI",
        "CDLXII",
        "CDLXIII",
        "CDLXIV",
        "CDLXV",
        "CDLXVI",
        "CDLXVII",
        "CDLXVIII",
        "CDLXIX",
        "CDLXX",
        "CDLXXI",
        "CDLXXII",
        "CDLXXIII",
        "CDLXXIV",
        "CDLXXV",
        "CDLXXVI",
        "CDLXXVII",
        "CDLXXVIII",
        "CDLXXIX",
        "CDLXXX",
        "CDLXXXI",
        "CDLXXXII",
        "CDLXXXIII",
        "CDLXXXIV",
        "CDLXXXV",
        "CDLXXXVI",
        "CDLXXXVII",
        "CDLXXXVIII",
        "CDLXXXIX",
        "CDXC",
        "CDXCI",
        "CDXCII",
        "CDXCIII",
        "CDXCIV",
        "CDXCV",
        "CDXCVI",
        "CDXCVII",
        "CDXCVIII",
        "CDXCIX",
        "D",
    ]

    labels = {
        "lower": LOWER,
        "arabic": ARABIC,
        "capital": CAPITAL,
        "romanette": ROMANETTE,
        "roman": ROMAN,
        "lower2": LOWER,
    }

    return labels[label_type]


def get_permissible(label_type, status, outline_depth):
    this_level = status[label_type]
    offset = depth_permission(status["depth"], outline_depth[label_type])
    return get_labels(label_type)[this_level + offset]


def number_of_tabs(number):
    """Returns a string with number tabs in it"""
    tabs = ""
    for _ in range(number):
        tabs = tabs + "\t"
    return tabs


def build_subsection(status, outline_depth):
    """
    Build the full subsection cite from status.
    Returns a string with a fully parenthetical subsection, e.g., the "(c)(2)(A)"
    to go in "#1798.135(c)(2)(A)"
    """
    subsection = ""
    for cite_depth in range(2, status["depth"] + 1):

        ilabel = get_key(cite_depth, outline_depth)
        subsection += "(" + get_labels(ilabel)[status[ilabel]] + ")"

    return subsection


def indent_statute(filtered_statute, law_info):
    """add indentation to input string `content` (which is a list of lines)

    `indented` is a list: [style, cite, indentation level, label, text]
    """

    indented = []

    label_depth = law_info["label_hierarchy"]

    provisions = extract_labels(filtered_statute, law_info)

    # status is a dictionary that tracks the current count on each level of
    # of numbering.
    status = {"depth": 0}

    # outline_depth specifies the indentation depth for each content type,
    # including headings, text without a label, and text with a label.
    outline_depth = {"heading": 0, "none": 1}

    # fill in the rest from label_depth
    for i in range(0, len(label_depth)):

        # beginning status for all is zero.
        status[label_depth[i]] = 0

        # Headings and none are above labels in the outline hierarchy
        outline_depth[label_depth[i]] = i + 2

    for i, (matches, section, label, text) in enumerate(provisions):

        # generate a list of allowed labels under the current scheme
        permissible = [
            get_permissible(label_depth[i], status, outline_depth)
            for i in range(0, len(label_depth))
        ]

        # Headings reset status (i.e., the current indentation level).
        if matches[0] == "bill_heading":
            status = reset_status(0, status, outline_depth)
            indented.append(("BILL_HEADING", section, 1, "", text))

        elif matches[0] == "law_heading":
            status = reset_status(0, status, outline_depth)
            indented.append(("LAW_HEADING", section, 1, "", text))

        # if there's no label, keep current level of indentation
        elif matches[0] == "none":
            # print(matches, section, label, text)
            indented.append(("NONE", "cite", status["depth"], "", text))  # fix cite

        # if the label is allowed under the pattern
        elif label in permissible:

            # if there is one matching pattern, set correct_match and move on.
            if permissible.count(label) == 1:
                correct_match = label_depth[permissible.index(label)]

            # if there is more than one matching pattern, figure out which one is right
            # by looking ahead to the next label.
            elif permissible.count(label) > 1:

                collisions = []

                for j, lab in enumerate(permissible):
                    if lab == label:
                        collisions.append(label_depth[j])

                next_label = provisions[i + 1][1]

                pattern_works = []

                for pattern in collisions:

                    hypo_status = copy.deepcopy(status)
                    hypo_status[pattern] += 1

                    new_permissible = get_permissible(
                        pattern, hypo_status, outline_depth
                    )

                    # print(f"pattern: {pattern}\nhypo_status: {hypo_status}\nnew_permissible: {new_permissible}")

                    hypo_permissible = list(permissible)
                    hypo_permissible.append(new_permissible)
                    print(hypo_permissible)
                    print(provisions[i + 1])
                    if next_label in hypo_permissible:
                        pattern_works.append(pattern)

                if len(pattern_works) == 1:
                    # print(f"pattern_works: {pattern_works}")
                    correct_match = pattern_works[0]

            if status["depth"] > outline_depth[correct_match]:
                status = reset_status(
                    outline_depth[correct_match], status, outline_depth
                )

            status[correct_match] += 1
            status["depth"] = outline_depth[correct_match]

            subsection = build_subsection(status, outline_depth)

            indented.append(
                ("TEXT", section + subsection, status["depth"], label, text)
            )
        else:

            indented.append(
                ("INDENTERROR", "cite", status["depth"], label, text)
            )  # fix cite

    return indented


def hyperlink(indented, law_info):

    new_html = []

    indent_style = {
        0: "MsoNormal",
        1: "MsoNormal",
        2: "MsoNormal",
        3: "Sub2",
        4: "Sub3",
        5: "Sub4",
        6: "Sub5",
    }

    try:
        defined_superterms = law_info["defined_superterms"]
    except KeyError:
        defined_superterms = {}

    try:
        defined_subterms = law_info["defined_subterms"]
    except KeyError:
        defined_subterms = {}

    for (style, cite, tabs, label, text) in indented:

        if label != "":
            if style == "TEXT":
                label_text = f"<a href = '#{cite}' class = 'clean'><strong>({label})</strong></a>"
            elif style == "INDENTERROR":
                label_text = f"<strong>({label})</strong>"
        else:
            label_text = ""

        line = text.strip()

        if style == "TEXT" or style == "INDENTERROR" or style == "NONE":

            line = f"{label_text} {line}"

            # Link and bold internal cites            
            def section_tweak(match):
                cite_block = match.group(1)
                end_block = match.group(2)
                if match.group(1).endswith("."):
                    # Remove trailing period on the end of section.
                    cite_block = cite_block[:-1]
                    end_block = "." + end_block

                return f" <a href = '#{cite_block}' class='heading'>{cite_block}</a>{end_block}"

            # pass function section_tweak as an argument to re.sub.
            line = re.sub(
                r" (1798\.1[\d\.]{2,7})([^\d])",
                section_tweak,
                line,
            )

            # Keep defined terms links out of headings because they create
            # nested href links which breaks the links.
            # Todo: Subterms and superterms aren't really the right approach.
            # Instead the way to do it is parse through the lines with
            # Beautiful soup and then you can determine whether each found
            # instance of sub-term is already inside a link.

            for term in defined_superterms:
                line = line.replace(
                    term,
                    f'<a href = "{defined_superterms[term]}" class = "clean">{term}</a>',
                )
                line = line.replace(
                    term.capitalize(),
                    f'<a href = "{defined_superterms[term]}" class = "clean">{term.capitalize()}</a>',
                )

            for term in defined_subterms:
                line = re.sub(
                    rf"([^>]){term}",
                    f'\g<1><a href = "{defined_subterms[term]}" class = "clean">{term}</a>',
                    line,
                )
                line = re.sub(
                    rf"([^>]){term.capitalize()}",
                    f'\g<1><a href = "{defined_subterms[term]}" class = "clean">{term.capitalize()}</a>',
                    line,
                )

        # Link and bold the headings
        elif style == "BILL_HEADING":
            line = f"<a href = '#{cite}' class='heading'><strong>{line}</strong></a>"

        elif style == "LAW_HEADING":
            line = f"<a href = '#{cite}' class='heading'><strong>{line}</strong></a>"

        line = line_cite(line, cite, indent_style[tabs])

        if style == "INDENTERROR":
            line = f"<div style='color:red'>{line}</div>"

        new_html.append(line)
    return new_html


def filter_html(html_content):

    filtered_statute = []

    # remove newlines because they aren't relevant for Beautful Soup and
    # they were causing errors in parsing some laws.
    newlines_removed = html_content.replace("\n", "")

    # Put the html into a Beautiful Soup object.
    soup = BeautifulSoup(newlines_removed, "html.parser")
    headings = soup.find_all(["h3", "h4", "h5", "h6", "p"])
    for line in headings:
        # print(type(line))
        style = line.get("style", "")
        pattern = re.compile(r"margin-left\s*:\s*\d+\.?\d*em")
        line_text = line.get_text().strip()
        if line.name == "h3":
            filtered_statute.append(("bill_heading", "", line_text))
        elif line.name == "h4":
            filtered_statute.append(("title", "", line_text))
        elif line.name == "h5":
            filtered_statute.append(("article", "", line_text))
        elif line.name == "h6":

            section = line_text

            # Remove trailing period on the end of section.
            if section.endswith("."):
                section = section[:-1]

            filtered_statute.append(("law_heading", section, line_text))
        elif "style" in line.attrs and (style == "margin:0;display:inline;" or pattern.search(style)):

            # This is standard space -------------------v
            triple_subsection = re.match(
                r"^(\(.{1,3}\))[  ](\(.{1,3}\))[  ](\(.{1,3}\).*)", line_text
            )
            double_subsection = re.match(
                r"^(\(.{1,5}\))[  ](\(.{1,5}\).*)", line_text
            )
            # This is a non-breaking space or something--^

            if triple_subsection:

                first_subsection = triple_subsection.group(1)
                second_subsection = triple_subsection.group(2)
                third_subsection = triple_subsection.group(3)

                filtered_statute.append(("paragraph", "", first_subsection))
                filtered_statute.append(("paragraph", "", second_subsection))
                filtered_statute.append(("paragraph", "", third_subsection))

            # put sub-sections on different lines.

            elif double_subsection:

                first_subsection = double_subsection.group(1)
                second_subsection = double_subsection.group(2)

                filtered_statute.append(("paragraph", "", first_subsection))
                filtered_statute.append(("paragraph", "", second_subsection))

            else:
                filtered_statute.append(("paragraph", "", line_text))

    # pprint(filtered_statute) #for debugging

    return filtered_statute

def filter_txt(law_text, law_info):

    content_type_re = {}
    filtered_statute = []

    with open(law_text) as f:
        content = f.readlines()

    heading_matches = []

    for line in content:
        category_re = {
            law_info["section_regex"]: "law_heading",
            "(SEC. [\d\d]{1,2}|SECTION [\d\d]{1,2})(.*)": "bill_heading",
        }
        for key in category_re:

            # create dict going the other direction to use later.
            content_type_re[category_re[key]] = key

            # if there's a match, add to heading_matches list.
            if re.match(key, line):
                heading_matches.append(category_re[key])

        if "law_heading" in heading_matches:

            law_section_heading = re.match(content_type_re["law_heading"], line)

            # Pull section number out of regex
            section = law_section_heading.group(1).strip()

            # Remove trailing period on the end of section.
            if section.endswith("."):
                section = section[:-1]

            filtered_statute.append(("law_heading", section, line))

        elif "bill_heading" in heading_matches:
            bill_section_heading = re.match(content_type_re["bill_heading"], line)

            section = bill_section_heading.group(1).strip()

            filtered_statute.append(("bill_heading", section, line))

        else:

            filtered_statute.append(("paragraph", "", line))

        heading_matches = []

    return filtered_statute


def format_statute(law_text, law_info, template, final_name):

    if law_text.endswith(".txt"):

        filtered_statute = filter_txt(law_text, law_info)
        title = law_info['title']

    elif law_text.endswith(".html"):

        # use Beautiful Soup to parse the HTML and identfy content types.
        with open(law_text) as f:
            html_content = f.read()

        filtered_statute = filter_html(html_content)

    elif law_text.startswith("http"):  # replace with proper URL regex match

        statute = requests.get(law_text)
        filtered_statute = filter_html(statute.text)

        # Extract title from filtered statute
        titles = [line for line in filtered_statute if line[0]=="title" or line[0]=="article"]
        title = titles[-1][2]

    indented = indent_statute(filtered_statute, law_info)
    # print(indented)
    new_html = hyperlink(indented, law_info)

    template = open(f"templates/{template}").read()
    ccpa_revised = re.sub("=========HERE===========", "".join(new_html), template)
    ccpa_revised = re.sub("\[~~TITLE~~\]", title, ccpa_revised)

    return ccpa_revised


default_law_info = {
    "label_hierarchy": {
        0: "lower",
        1: "arabic",
        2: "capital",
        3: "romanette",
        4: "roman",
    },
}

if __name__ == "__main__":
    leginfo_url = input("Enter leginfo url for statute (bills won't work yet): ")
    linked_text = format_statute(leginfo_url, default_law_info, "index_template_general.html", "generic_out.html")
    with open("statute.html", "w", encoding="utf-8") as file:
        file.write(linked_text)
