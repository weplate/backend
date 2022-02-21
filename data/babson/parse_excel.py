import os
import re
from re import Match
import json

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet

OUT_FILE_PATH = 'meal_items.json'

SCHOOL_ID = 10


def main():
    print(os.getcwd())
    main_sheet: Worksheet = load_workbook('Nutrition_Facts_as_of_Feb_20.xlsx', read_only=True)['Report']
    micros_sheet: Worksheet = load_workbook('Additional_nutrition_facts_as_of_Feb_20.xlsx', read_only=True)['Report']

    meal_items = {}

    NUM = r'(([0-9]+)(\/[0-9]+)?)'
    def parse_num(matches: Match):
        mat = matches.group(1)
        if '/' in mat:
            n, d = mat.split('/')
            return float(n) / float(d)
        else:
            return float(mat)

    bad_units = set()
    def parse_portion(value):
        if m := re.search(rf'{NUM} cup', value):
            return parse_num(m) * 236.588, False
        elif m := re.search(rf'{NUM} pint', value):
            return parse_num(m) * 473, False
        elif m := re.search(rf'{NUM} tbsp', value):
            return parse_num(m) * 14.7866, False
        elif m := re.search(rf'{NUM} tsp', value):
            return parse_num(m) * 4.92892, False
        elif m := re.search(rf'{NUM} floz', value):
            return parse_num(m) * 29.5735, False
        elif m := re.search(rf'[0-9] ladle-{NUM}oz', value):
            return parse_num(m) * 29.5735, False
        else:
            bad_units.add(value)
            return -1, True


    # Read macros
    cur_station = None
    for row in main_sheet.iter_rows(13, 1039):
        def get_col(col):
            return row[col].value

        def num_col(col):
            val = get_col(col)
            if val is None: return 0
            else:
                only_num = re.sub(r'[^0-9.]', '', val)
                return float(only_num) if only_num else 0

        if get_col(1) is None:
            cur_station = get_col(0)
        else:
            portion, p_err = parse_portion(get_col(3))
            if not p_err:
                meal_items[get_col(0)] = {
                    'name': get_col(0),
                    'station': cur_station,
                    'portion_weight': num_col(6),
                    'portion_volume': portion,
                    'ingredients': [],
                    'school': SCHOOL_ID,

                    'calories': num_col(7),
                    'protein': num_col(9),
                    'total_fat': num_col(10),
                    'saturated_fat': num_col(11),
                    'sugar': num_col(12),
                    'fiber': num_col(14),
                    'sodium': num_col(16),
                    'potassium': num_col(17),
                    'calcium': num_col(18),
                    'iron': num_col(19),
                }

    for row in micros_sheet.iter_rows(13, 1021):
        def get_col(col):
            return row[col].value

        def num_col(col):
            val = get_col(col)
            if val is None: return 0
            else:
                only_num = re.sub(r'[^0-9.]', '', val)
                return float(only_num) if only_num else 0

        if get_col(0) in meal_items:
            meal_items[get_col(0)] |= {
                'vitamin_d': num_col(7),
                'vitamin_c': num_col(9),
                'vitamin_a': num_col(10),
                'cholesterol': num_col(13),
            }

    with open(OUT_FILE_PATH, 'w') as f:
        json.dump(meal_items, f)

    print('-- Bad Units --')
    for unit in sorted(bad_units):
        print(unit)


if __name__ == '__main__':
    main()
