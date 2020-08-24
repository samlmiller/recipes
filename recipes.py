import json
import os
import pprint as pretty

"""
Dictionary for Recipe File
1. All ingredients should be lower case
2. Each ingredient is the key, with the amount and unit amount as an associated value
3. Possible units:
    tsp, 
    tbsp, 
    cup/liquid, 
    cup/solid, 
    oz/liquid, 
    oz/solid, 
    lbs, 
    single (used in reference to the ingredient itself e.g. tortilla == single),
    clove,
    bunch (used for vegetables such as cilantro and other herbs, or asparagus)
"""

class ShoppingList(object):

    def __init__(self, recipe):
        with open(recipe, 'r') as infile:
            self.recipes = json.load(infile)

        invalid = self._lint_recipes()
        if invalid:
            print("Fix recipe list before proceeding")
            raise Exception("Did not pass linting test")

        self.selected_recipes = set()
        self.shopping_list = {}
        self.convertable_list = {}
        self.nonconvertable_list = {}
        self.manual_list = {}
        self.spice_list = set()
        print("Recipe list has been loaded! Call \"help\" for more instructions :)")

    @staticmethod
    def check_number(val):
        if isinstance(val, float) or isinstance(val, int):
            return True

        return False

    @staticmethod
    def check_list(list_):
        for item in list_:
            if not ShoppingList.check_number(item):
                passed_check, fail_string = ShoppingList.check_case(item, case_type='lower')
                if passed_check:
                    continue
                else:
                    print(f"List check failed for {item}")
                    return False
            else:
                continue

        return True

    @staticmethod
    def name_case(word):
        if not isinstance(word, str):
            return word

        return word[0].upper() + word[1:].lower()

    @staticmethod
    def lint_case(word, case_type='lower'):
        if ShoppingList.check_case(word=word, case_type=case_type):
            return word
        else:
            map_ = {'lower': word.lower(),
                    'upper': word.upper(),
                    'name_case': ShoppingList.name_case(word=word)}
            return map_[case_type]

    @staticmethod
    def check_case(word, case_type='lower'):
        CASE_TYPES = ['lower', 'upper', 'name']
        if case_type not in CASE_TYPES:
            return False, f"Invalid case type comparison: {case_type}!"

        if (word != word.lower() and case_type == 'lower') or \
           (word != word.upper() and case_type == 'upper') or \
           (word != ShoppingList.name_case(word) and case_type == 'name'):
            print_str = f"Invalid Case: {word}"
            return False, print_str
        else:
            return True, ''

    @classmethod
    def convert_unit(cls, amount, start, target):
        if target not in ShoppingList.get_unit_list(type_='convertable'):
            print('Error converting units')
            return False
        else:
            conversion_table = ShoppingList.get_conversion_table()
            conversion_factor = conversion_table[start][target]
            return amount * conversion_factor

    @classmethod
    def get_unit_list(cls, type_='all'):
        accepted_types = ['all', 'convertable', 'nonconvertable']
        if type_ not in accepted_types:
            raise Exception(f"Supplied type -- {type_} -- not in {accepted_types}")

        unit_list = ['tsp', 'tbsp', 'cup/liquid', 'cup/solid', 'oz/liquid', 'oz/solid', \
                     'lbs', 'single', 'clove', 'bunch', 'slice']
        convertable_list = ['tsp', 'tbsp', 'cup/liquid', 'cup/solid', 'oz/liquid', 'oz/solid', 'lbs']
        non_convertable_list = [each for each in unit_list if each not in convertable_list]

        return_map = {'all': unit_list,
                      'convertable': convertable_list,
                      'nonconvertable': non_convertable_list}
        return return_map[type_]

    @classmethod
    def get_recipe_key_list(cls):
        recipe_keys = ['recipe', 'ingredients', 'rating', 'spices', 'url', 'category', 'servings']
        return recipe_keys

    @classmethod
    def get_conversion_table(cls):
        return {'oz/solid': {'cup/solid': 0.125,
                             'tbsp': 2,
                             'tsp': 6,
                             'lbs': 0.0624
                             },
                'oz/liquid': {'cup/liquid': 0.125,
                              'tbsp': 2,
                              'tsp': 6,
                              'pint': 1/16.0,
                              'quart': 1/64.0,
                              'gallon': 1/256.0
                              },
                'cup/solid': {'oz/solid': 8,
                              'tbsp': 16,
                              'tsp': 48,
                              'lbs': 0.5,
                              },
                'cup/liquid': {'oz/liquid': 8,
                               'tbsp': 16,
                               'tsp': 48,
                               'pint': 0.5,
                               'quart': 0.25,
                               'gallon': 0.25/4.0
                               },
                'tbsp': {'cup/solid': 1/16.0,
                         'cup/liquid': 1/16.0,
                         'oz/solid': 0.5,
                         'tsp': 3,
                         'lbs': 0.0315
                         },
                'tsp': {'cup/solid': 1/48.0,
                        'oz/liquid': 1/48.0,
                        'tbsp': 0.3333,
                        'oz/solid': 0.16667,
                        'lbs': 0.0105
                        },
                'lbs': {'cup/solid': 2,
                        'tbsp': 32,
                        'tsp': 96,
                        'oz/solid': 16
                        }
                }

    def _lint_recipes(self):

        def check_keys(recipe):
            master_key_list = ShoppingList.get_recipe_key_list().sort()
            compare_key_list = [each for each in recipe.keys()].sort()
            if master_key_list != compare_key_list:
                print(f"Recipe keys are incomplete/invalid!\nExpecting: {master_key_list}\nReceived: {compare_key_list}")
                return False

            return True

        def check_values(recipe):
            # Validation type map
            validation_json_key_map = {'no_validation': ['ingredients', 'recipe'],
                                       'number': ['rating', 'servings'],
                                       'list': ['spices']
                                       }
            for key in ShoppingList.get_recipe_key_list():
                # Pass check for ingredients and recipe name
                if key in validation_json_key_map['no_validation']:
                    continue
                # Check for valid number
                elif key in validation_json_key_map['number']:
                    val = float(recipe[key])
                    passed_check = ShoppingList.check_number(val)
                # Check list of valid spices name
                elif key in validation_json_key_map['list']:
                    passed_check = ShoppingList.check_list(recipe[key])
                # Check category, and url (single list of strings to be lowercase)
                else:
                    passed_check, fail_string = ShoppingList.check_case(recipe[key], case_type='lower')
                    if passed_check:
                        continue
                if not passed_check:
                    print(f"Recipe values are incomplete/invalid! Check case for {recipe['recipe']}: {recipe[key]}!")
                    return False

            return True

        # Master flag determines if anything is wrong, in which case it returns False,
        # so nothing else will continue until corrected
        master_flag = False
        for each in self.recipes['recipes']:
            if not check_keys(each) or not check_values(each):
                break

            # First flag is used to determine whether the
            # recipe name has been printed out yet (should
            # only be printed once)
            first = True
            # Cycle through ingredients to ensure
            # case and key names / values are consistent
            for ing in each['ingredients']:
                for key, value in ing.items():
                    # Linter flag is used to keep track of
                    # of whether the current ingredient name
                    # needs to be printed out or not (should
                    # only be printed out once)
                    linter_flag = False
                    passed_check, fail_string = ShoppingList.check_case(key, case_type='lower')
                    if first and not passed_check:
                        print(f"Recipe: {each['recipe']}")
                        print(fail_string)
                        first = False
                        linter_flag = True

                    # Cycle through an ingredient row to guarantee formatting and consistency
                    for k, v in value.items():
                        if k not in ('amount', 'unit'):  # These are the allowable ingredient keys
                            if first:
                                print(f"Recipe: {each['recipe']}")
                                first = False

                            print(f"Ingredient: {key}\n    Invalid key name: {k}")
                            linter_flag = True
                        if k == 'unit':
                            # If looking at units, ensure they adhere to the accepted list
                            if v not in ShoppingList.get_unit_list(type_='all'):
                                if not linter_flag:
                                    if first:
                                        print(f"Recipe: {each['recipe']}")
                                        first = False

                                    print(f"Ingredient: {key}")
                                    linter_flag = True

                                print(f"    Invalid unit name: {v}")
                        else:
                            # Ensure that the amount for the ingredient is numerical
                            if not ShoppingList.check_number(v):
                                if not linter_flag:
                                    if first:
                                        print(f"Recipe: {each['recipe']}")
                                        first = False

                                    print(f"Ingredient: {key}")
                                    linter_flag = True

                                print(f"    Invalid amount type: {type(v)}")

                    if linter_flag:
                        master_flag = True

        return master_flag

    def print_recipes(self, ingredients=False, verbose=False, help=False, *args, **kwargs):
        """kwargs = [rating, url, spices, category]"""
        """args = [pared] for pared down list"""
        if help:
            ShoppingList._method_help(method_name=ShoppingList.print_recipes.__name__,
                                      params=['ingredients -- if set to True then it will print out all the ingredients with the recipe',
                                              'verbose -- if set to True then amounts will be printed out alongside ingredients (ingredients must be True)',
                                              'kwargs -- can print out other specific information if desired such as '
                                              '"rating", "spices", "category", "url", "servings" which serve as the keyword, and T/F for the value.'],
                                      notes="Use to look at all recipes :)")
            return

        for each in self.recipes["recipes"]:
            print(f"Recipe: {each['recipe']}")
            if ingredients:
                print("Ingredients:")
                for ing in each['ingredients']:
                    for key, value in ing.items():
                        print(f"    {key}")
                        if verbose:
                            for k, v in value.items():
                                print(f"        {k}: {v}")

                print(f"Spices: {each['spices']}")

            for kwarg in kwargs:
                if kwarg not in ['rating', 'spices', 'category', 'url', 'servings']:
                    pass
                else:
                    if kwargs[kwarg] == True:
                        print(f"    {ShoppingList.name_case(kwarg)}: {ShoppingList.name_case(each[kwarg])}")

    def select_recipes(self, help=False):
        if help:
            ShoppingList._method_help(method_name=ShoppingList.select_recipes.__name__,
                                      notes="Used to select recipes to make for the shopping list :D\nNOTE: this doesn't actually add the ingredients. You need to call \"prepare_list\" to do that!")
            return

        recipe_keys = [each['recipe'].lower() for each in self.recipes['recipes']]
        print("Select recipes you wish to order or search with the following commands!")
        print("1. 'all' -- print out all available recipes by name")
        print("2. 'rating x' -- print out all available recipes that have a rating >= to x")
        print("3. 'category y' -- print out all available recipes that fall in category y")
        print("4. 'remove z' -- remove recipe z from the selected list")
        print("5. 'current' -- print current list")
        print("6. 'add b' -- add recipe b to the list")
        print("7. 'done' -- finish adding all of the recipes")
        while True:
            action = input("Either enter recipe or select a command: ")
            print('')
            primary = ShoppingList.lint_case(action.split(' ')[0], case_type='lower')
            # Add to the list
            if primary == 'add':
                selected_recipe = ' '.join(action.lower().split(' ')[1:])
                for sr in selected_recipe.split(','):
                    sr = sr.lstrip().rstrip()
                    if sr not in recipe_keys:
                        print(sr, recipe_keys)
                        print("Your recipe is not in the recipe list. Add it to the list before adding. Choose next recipe :)")
                        continue
                    else:
                        self.selected_recipes.add(sr)

            # Remove from list
            if primary == 'remove':
                selected_recipe = ' '.join(action.lower().split(' ')[1:])
                if selected_recipe in self.selected_recipes:
                    self.selected_recipes.remove(selected_recipe)
                else:
                    print(f"{selected_recipe} not in {selected_recipes}!")

            # Print out all recipes
            if primary == 'all':
                self.print_recipes(recipes=self.recipes)

            # Print out current recipes
            if primary == 'current':
                k = 1
                for recipe in self.selected_recipes:
                    print(f"{k}. {recipe}")
                    k += 1

            # Print out based on rating
            if primary == 'rating':
                try:
                    min_score = float(action.lower().split(' ')[1])
                except Exception:
                    print("Please enter a valid rating!")
                    continue

                i = 1
                for recipe in self.recipes['recipes']:
                    if float(recipe['rating']) >= min_score:
                        print(f"{i}. {recipe['recipe']} -- {recipe['rating']}/10")
                        i += 1

            # Print out based on category
            if primary == 'category':
                cat = ' '.join(action.lower().split(' ')[1:])
                j = 1
                for recipe in self.recipes['recipes']:
                    if recipe['category'] == cat:
                        print(f"{j}. {recipe['recipe']}")
                        j += 1

            # Done
            if primary == 'done':
                break

            os.system('clear')

        return True

    def _gather_ingredients(self, ingredients, serving_size=2):
        for ingredient in ingredients:
            for k, v in ingredient.items():
                main = k
                amt = v['amount']
                unit = v['unit']
                if unit in ShoppingList.get_unit_list(type_='convertable'):
                    if main not in self.convertable_list:
                        self.convertable_list[main] = {'amount': amt, 'unit': unit}
                    elif self.convertable_list[main]['unit'] == unit:
                        self.convertable_list[main]['amount'] += amt
                    else:
                        amt = ShoppingList.convert_unit(amount=amt, start=unit, target=self.convertable_list[main]['unit'])
                        if not amt:
                            raise Exception(f"Error converting units for {main} with units {unit}!")

                        self.convertable_list[main]['amount'] += amt
                else:
                    if main not in self.nonconvertable_list:
                        self.nonconvertable_list[main] = {'amount': amt, 'unit': unit}
                    elif self.nonconvertable_list[main]['unit'] == unit:
                        self.nonconvertable_list[main]['amount'] += amt
                    else:
                        raise Exception("Multiple nonconvertable types --> solve how to do please :)")

    def prepare_list(self, help=False):
        if help:
            ShoppingList._method_help(method_name=ShoppingList.prepare_list.__name__,
                                      notes="Call this once you've chosen your recipes to add all the appropriate\ningredients to the shopping list :)")
            return

        for recipe in self.recipes['recipes']:
            if recipe['recipe'].lower() not in self.selected_recipes:
                continue
            else:
                self._gather_ingredients(ingredients=recipe['ingredients'])
                for spice in recipe['spices']:
                    self.spice_list.add(spice)

        return True

    def _sort_lists(self):
        self.shopping_list = {}
        all_keys = sorted(set(list(self.convertable_list.keys()) + list(self.nonconvertable_list.keys())))
        lists = [self.convertable_list, self.nonconvertable_list]
        for key in all_keys:
            i = 0
            for l in lists:
                if key in l:
                    if i == 0:
                        self.shopping_list[key] = l[key]
                        i += 1
                    else:
                        key_rep = key + i * '_'
                        self.shopping_list[key_rep] = l[key]

    def pprint_shopping_list(self, help=False):
        if help:
            ShoppingList._method_help(method_name=ShoppingList.pprint_shopping_list.__name__,
                                      notes="Print out the current shopping list, prettily :P")
            return

        self._sort_lists()
        if self.shopping_list:
            print("MAIN INGREDIENTS / ITEMS\n")
            for k, v in self.shopping_list.items():
                print(f"{ShoppingList.name_case(k)} - {v['amount']} {v['unit']}")

        if self.spice_list:
            print("\nSPICE LIST :D\n")
            for spice in self.spice_list:
                print(ShoppingList.name_case(spice))

    def add_items(self, help=False, **kwargs):
        if help:
            ShoppingList._method_help(method_name=ShoppingList.add_items.__name__,
                                      params=['**kwargs -- the keyword acts as the ingredient and the value is the amount followed by a space and then the unit'],
                                      notes="Use to add single ingredients or items as opposed to a recipe.\nTo see allowable units, call \"get_unit_list\"")
            return

        for ingredient, amounts in kwargs.items():
            ingredient = ShoppingList.lint_case(word=ingredient, case_type='lower')
            try:
                amount = float(amounts.split(' ')[0])
            except TypeError:
                raise TypeError(f"Cannot cast {amount} to a float!")

            unit = amounts.split(' ')[1]
            if not ShoppingList.check_number(amount):
                raise Exception(f"Invalid ingredient amount for {ingredient} -- {amount} {unit}")
            elif unit not in ShoppingList.get_unit_list(type_='all'):
                raise Exception(f"Invalid unit supplied for {ingredient} -- {amount} {unit}")

            self._gather_ingredients(ingredients=[{ingredient: {'amount': amount, 'unit': unit}}])

    def clear(self, help=False):
        if help:
            ShoppingList._method_help(method_name=self.clear.__name__,
                                      notes="Call this method to empty the shopping list")
            return

        self.__init__()

    def print_recipe(self, recipe=None, help=False):
        if help:
            ShoppingList._method_help(method_name=self.print_recipe.__name__,
                                      params=['recipe - name of recipe to get'],
                                      notes="Only returns one full recipe object at a time")
            return

        while not recipe:
            recipe = input("Please select a recipe! ")

        linted_recipe = ShoppingList.lint_case(word=recipe, case_type='lower')
        linted_master_list = [ShoppingList.lint_case(word=each['recipe'], case_type='lower') for each in self.recipes['recipes']]
        if linted_recipe not in linted_master_list:
            print(linted_recipe, linted_master_list)
            print(f"{ShoppingList.name_case(recipe)} not found in Recipes list!")
        else:
            for rec in self.recipes['recipes']:
                if rec['recipe'].lower() == linted_recipe:
                    print(rec)

    @staticmethod
    def _method_help(method_name, params=None, notes=None):
        print(f"========== {method_name} ==========\n")
        if params:
            print("Parameters")
            i = 1
            for param in params:
                print(f"{i}. {param}")
                i += 1

        if notes:
            print("\nNotes / Comments")
            print(notes)

        if not params and not notes:
            print("No parameters possible!")

        print("\n========== END ==========")

    def help(self):
        print("========== HELP WINDOW ==========\n")
        print("Current methods:")
        print("\n N.B. \"help\" can be called with all methods below to explain usage in depth!\n")
        print("1. print_recipes @params [ingredients, verbose] -- used to view all recipes")
        print("2. select_recipes @params [] -- used to select recipes")
        print("3. prepare_list @params []  -- used to gather ingredients for selected recipes")
        print("4. pprint_shopping_list @params [] -- print out the final list of ingredients")
        print("5. add_items @params [help, **kwargs] -- add specific items")
        print("6. clear @params [] -- clear the entire shopping list")
        print("7. print_recipe @params [recipe] -- fetch the recipe object for a given recipe")
        print("\n========== END WINDOW ==========\n")

#TODO: adjust_serving_size