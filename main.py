import requests
from config import API_KEY

pantry = []
my_list = {}  # Dictionary of saved recipes. name -> Spoonacular id


def add_to_pantry(ingredient):
    """Add an item to the pantry. If it's already there, do nothing"""
    if ingredient in pantry:
        print("Ingredient is already in pantry")
    else:
        pantry.append(ingredient)
        print(f"{ingredient} has been added to the pantry")


def remove_from_pantry(ingredient):
    """Remove an item from the pantry. If it's not there, do nothing"""
    for item in pantry:
        if item.lower() == ingredient.lower():
            pantry.remove(item)
            print(f"Removed {item} from the pantry")
            return
    print(f"Couldn't find {ingredient} in the pantry")


def print_pantry():
    """List out the current items in the pantry"""
    if len(pantry) == 0:
        print("Your pantry is empty")
    else:
        for food in pantry:
            print(food)


def add_to_list(recipe, id):
    """Add an item to the wish list. If it's already there, do nothing"""
    if recipe in my_list:
        print("Ingredient is already in your list")
    else:
        my_list[recipe] = id
        print(recipe, "was added to your list")


def print_list():
    """Print the recipes in the user's list"""
    if len(my_list) == 0:
        print("Your list is empty.")
    else:
        counter = 1
        for recipe in my_list:
            print(f"{counter}. {recipe}")
            counter += 1


def api_get_request(url, params):
    """Completes a get request to the Spoonacular API."""
    request = requests.get(url, params)
    if request.status_code == 402:
        print("Error. You've met the daily quota for API requests. Please try "
              "again tomorrow.")  # Refreshes at 7pm CT
        return None
    elif request.status_code != 200:
        print(f"Error {request.status_code}. Please try again")
        return None
    return request.json()


def get_number_from_user(input_string, max_num):
    """Helper method to get a valid number from user
    max_num is the highest number the user may enter
    """
    try:
        choice = int(input(input_string))
    except ValueError:
        choice = -1
    while choice <= 0 or choice > max_num:
        try:
            choice = int(input("Please enter a valid number: "))
        except ValueError:
            continue
    return choice


def search_from_pantry():
    """Searches for recipes that can be made using the items that are currently
    in the user's pantry. Also gives the user the option to view the
    instructions for one of the result recipes.
    """
    ingredient_string = ",+".join(pantry)

    url = "https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "ingredients": ingredient_string,
        "apiKey": API_KEY,
        "ranking": 2,  # Prioritizes minimizing missed ingredients
        "number": 5,
        "ignorePantry": "true"
    }
    print("Loading...")
    result = api_get_request(url, params)

    if result is None:
        return  # Error
    if len(result) == 0:
        print("Sorry, no matches found.")
        return

    if result[0]["missedIngredientCount"] != 0:
        # First recipe doesn't match, therefore there are no perfect matches
        print("No recipes match, here are the closest:\n")
    else:
        print("Results:\n")

    recipe_names = []  # Used for adding to list later
    recipe_ids = []  # Used for adding to list later
    for recipe in result:
        recipe_names.append(recipe["title"])
        recipe_ids.append(recipe["id"])
        print(recipe["title"], "Ingredients:", sep="\n")
        for item in recipe["missedIngredients"]:
            print("MISSING -", item["original"])
        for item in recipe["usedIngredients"]:
            print(item["original"])
        print()

    save_to_list(recipe_names, recipe_ids)


def search_from_name(name):
    """Searches for recipes that match the passed name and displays them.
    Also gives the user the option to view the instructions for one of the
    result recipes.
    """
    url = "https://api.spoonacular.com/recipes/complexSearch"
    params = {
        "apiKey": API_KEY,
        "query": name,
        "number": 5
    }
    print("Loading...")
    result = api_get_request(url, params)
    if result is None:
        return  # Error
    if result["totalResults"] == 0:
        print("Sorry, no matches found.")
        return

    result_list = result["results"]  # List of recipes that have similar name
    recipe_names = []  # Used for adding to list later
    id_string = ""
    for item in result_list:  # Gets list of IDs that match
        recipe_names.append(item["title"])
        id_string += str(item["id"]) + ","
    id_string = id_string[:-1]  # Remove extra comma added at the end

    # Does a bulk search using the ids to get ingredients for all recipes found
    url = "https://api.spoonacular.com/recipes/informationBulk"
    params = {
        "apiKey": API_KEY,
        "ids": id_string
    }

    recipe_info = api_get_request(url, params)

    print("Results:\n")
    for recipe in recipe_info:
        print(recipe["title"], "Ingredients:", sep="\n")
        for ingredient in recipe["extendedIngredients"]:
            print(ingredient["original"])
        print()

    save_to_list(recipe_names, id_string.split(","))


def save_to_list(recipe_names, recipe_ids):
    """Prompts the user if they would like to add a recipe to their list. If
    yes, the user selects which recipe.
    The recipe options come from the output of search_from_pantry or
    search_from_name().
    Only called after search_from_pantry() or search_from_name()
    :param recipe_names: The list of names of recipes to display.
    :param recipe_ids: List of ids corresponding to recipe_names. Used for API
                       query.
    """
    choice = ""
    while choice != "y" and choice != "n"\
            and choice != "yes" and choice != "no":
        choice = input("Would you like to save any of these recipes to your "
                       "list? Enter y or n ").lower()
    if choice == "n" or choice == "no":
        return

    for i in range(len(recipe_names)):
        print(i + 1, ". ", recipe_names[i], sep="")
    choice = get_number_from_user("Enter the number of the recipe you would "
                                  "like to save: ", len(recipe_names))
    name = recipe_names[choice - 1]
    id = recipe_ids[choice - 1]
    my_list[name] = id

    print(f"\n{name} has been saved to your list.")


def get_instructions():
    """Prompts the user if they would like to see the instructions for a
    recipe in their list. If yes, the user selects which recipe and the
    instructions are output.
    """
    choice = ""
    while choice != "y" and choice != "n"\
            and choice != "yes" and choice != "no":
        choice = input("Would you like to view the instructions for any of "
                       "these recipes? Enter y or n ").lower()
    if choice == "n" or choice == "no":
        return

    # Gives the user choices for a recipe to view instructions
    choice = get_number_from_user("Enter the number of the recipe whose "
                                  "instructions you would like to view: ",
                                  len(my_list))
    # Turns the dictionary keys into a list and indexes using 0-based indexing
    id = my_list[list(my_list.keys())[choice - 1]]

    url = f"https://api.spoonacular.com/recipes/{id}/analyzedInstructions"
    params = {
        "apiKey": API_KEY
    }
    print("Loading...\n")
    result = api_get_request(url, params)

    if len(result) == 0:
        print("Sorry, I do not have the instructions for this recipe.")
    else:
        for step in result[0]["steps"]:
            print("Step ", step["number"], ". ", step["step"], sep="")


def main():
    print("Welcome to your Personal Culinary Assistant")
    print("Select menu option 7 to get help on how to use this program")
    while True:
        print("Menu:")
        print("1: Add a new ingredient to the pantry")
        print("2: Remove an item from the pantry")
        print("3: List current items in pantry")
        print("4: View your saved recipe list")
        print("5: Search for recipes to cook from current pantry ingredients")
        print("6: Search for a recipe by name")
        print("7: Help")
        print("8: Exit")

        # Prompts the user for (valid) menu choice
        choice = get_number_from_user("Enter your choice here: ", 8)
        print()

        match choice:
            case 1:
                item = input("Which ingredient would you like to add? ")
                add_to_pantry(item)
            case 2:
                item = input("Which ingredient would you like to remove? ")
                remove_from_pantry(item)
            case 3:
                print_pantry()
            case 4:
                print_list()
                if len(my_list) > 0:
                    get_instructions()
            case 5:
                search_from_pantry()
            case 6:
                name = input("What recipe would you like to search for? ")
                search_from_name(name)
            case 7:
                print("Welcome to your cooking aide! This program allows you\n"
                      "to find recipes to cook based on the ingredients you \n"
                      "currently have. All you have to do is add them to \n"
                      "your pantry, and the search feature will take care of\n"
                      "the rest. Alternatively, you can search for recipes \n"
                      "by name. After completing a search you can add \n"
                      "recipes to your list, and later you can look back at \n"
                      "them and view their cooking instructions. Enjoy!")
            case 8:
                break
        print()


if __name__ == '__main__':
    main()
