'''
This program helps a user manage an activity list and then search for the applicable businesses on Yelp leveraging the Yelp Fusion API. A user can associate an activity to a particular business category in order to search for businesses that will match that activity. 

The Yelp search will be conducted based on user provided criteria, such as search address, radius, and type of search (search by most reviewed businesses, highest rated businesses, or businesses closest to search address). The program will return the results of the Yelp search in a user friendly readable table. 
'''

import json
from yelpapi import YelpAPI
import config
from yelp_categories import CategoryTree
from google_maps import Map

class UI():

    '''
    A class to handle all the user interactions via the command line, including inputs and outputs.

    Attributes
    ----------
    a_list (ActivityList):
        The activity list
    b_dict (Category:YelpBusinessList{}):
        A dictionary containing a list of activity categories and their associated businesses
    option (int):
        The action option seelcted by the user
    address (str):
        The search address
    cat_tree_obj (CategoryTree):
        The category tree containing the mapping of all categories and their respective subcategories
    '''

    def __init__(self, categories_file):

        '''
        Constructs the UI object

        Parameters
        ----------
        categories_file (str):
            The JSON file name containing the categories

        Returns
        -------
        None
        '''

        self.a_list = ActivityList()
        self.b_dict = {}
        self.option = 0
        self.address = ''

        # Read in the business categories JSON file (from Yelp Fusion API website)
        with open(categories_file) as __file:
            __categories = json.load(__file) 

        self.cat_tree_obj = CategoryTree(__categories)

        __welcome_msg = "\nWelcome to Yelist, the first ever activity list aggregate search powered by Yelp!\nTo get started, please enter your first activity."
        print(__welcome_msg)

        # Add an activity to start the activity list
        self.add_activity()

    def user_input(self):

        '''
        The main method that is called to start the program, and calls other methods that handle the user interactions.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        
        # Display options and check for valid user input
        while self.option != 5:
            self.option = self.display_options()
            self.option = self.check_in_range(self.option, 5)
            if self.option == 1:
                self.add_activity()
            elif self.option == 2:
                self.remove_activity()
            elif self.option == 3:
                self.change_priority()
            elif self.option == 4:
                self.print_list()

        self.option = 0

        # Display Yelp search options and check for valid user input
        while self.option < 1:
            self.option = self.display_options(search=True)
            self.option = self.check_in_range(self.option, 3)

        # If no businesses were found, skip output and exit program
        if self.search_yelp(self.option) is None:
            pass

        # Else, print output and, if requested, open a map with directions
        else:
            self.print_yelp_output(self.option)
            self.open_map()

        print('\nExiting program... Thanks for using Yelist!\n')

    def show_categories(self):
        '''
        Displays the current list of categories and handles any traversals through the category tree while the user is selecting a category

        Parameters
        ----------
        None

        Returns
        -------
        category (Category):
            The selected activity category
        '''

        print('\nSelect a category for your activity. To continue to drill down into the sub-categories, enter the name of the category you want to explore further (case-sensitive). When you have decided on one of the categories displayed, enter "Select [category_name]". You can select any of the categories or sub-categories listed.\n')


        current_cats = self.cat_tree_obj.print_output 
        search_term = ''
        selected = ''
        search_stack = []

        # Print the initial list of categories
        [print(cat) for cat in sorted(current_cats.keys())]

        # While the user has not yet selected a category
        while selected != "select": 
            search_term = input('\nEnter a category, use "Select [category]" to select, or use "BACK" to go back up one category: ')
            print()

            # If the user wants to select the category
            if search_term[:6].lower() == "select":
                terms = search_term.split(" ", 1)
                selected = terms[0].lower()
                search_term = terms[1]

            # If the user wants to go back one category, pop the last search from the search_stack
            if search_term == "BACK":
                if search_stack:
                    current_cats = search_stack.pop() 
                    [print(cat) for cat in sorted(current_cats.keys())]
                    continue
                else:
                    print("You cannot go back any further.\n")

            found_flag = False

            for category in current_cats.keys():
                # Check if the searched category is in the list of currently displayed categories
                if search_term == category.title:
                    # If the user has selected a category, turn on the found_flag and break
                    if selected:
                        found_flag = True
                        break
                    # There are no more sub-categories to drill down into
                    if current_cats[category] == '':
                        print(f"There are no more sub-categories under {search_term}")
                    # If the category was found but the user did not use the select keyword, append the current search to the search_stack and print the next set of sub-categories
                    else:
                        search_stack.append(current_cats)
                        current_cats = current_cats[category]
                        [print(cat) for cat in sorted(current_cats.keys())]
                    found_flag = True
                    break
            
            # If there was no matching search term found
            if not found_flag:
                print("You did not enter a valid category or command (case-sensitive).\n")
                selected = ''

        return category

    def display_options(self, search=False):

        '''
        Prints the list of options when creating the activity list and when initiating the Yelp search and takes in user input

        Parameters
        ----------
        search (bool):
            Determines whether to display the activity list options (False) or the Yelp search options (True)

        Returns
        -------
        __list_of_options (str):
            The user input response to the activity list options
        OR
        __search_options (str):
            The user input response to the Yelp search options
        '''

        if type(search) != bool:
            raise Exception("search argument must be boolean")

        if search == False:
            __list_of_options = input("What would you like to do? Select one of the following options [1-5]:\n1. Add an activity to your current list\n2. Remove an activity from your current list\n3. Change the priority of an activity\n4. View your current activity list\n5. Search Yelp for places on your activity list\n")
            return __list_of_options

        elif search == True:
            __search_options = input("\nHow would you like to search? Select one of the following options [1-3]:\n1. Search by most reviews\n2. Search by highest rating\n3. Search by shortest distance\n")
            return __search_options

    def add_activity(self):

        '''
        Manages user interactions when the add activity option is selected. Calls ActivityList add_to_list() method

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''

        # Max size of activity list is 10
        if len(self.a_list) > 9:
            print("\nYour list is full (max size of 10). Remove an activity before adding another.\n")
            return

        # Ask user to input their desired activity string
        a_name = input("\nWhat activity will you be doing?\n")
        a_category = self.show_categories()
        a_prio = 0

        # If the search list is empty, automatically assign the activity a priority of 1
        if not self.a_list:
            a_prio = 1

        # Ask user for activity priority, check for valid user input, and add the activity to the activity list
        while a_prio < 1:
            a_prio = input(f"Assign a priority to this activity [1-{len(self.a_list)+1}]: ")
            a_prio = self.check_in_range(a_prio,len(self.a_list)+1)
        self.a_list.add_to_list(Activity(a_name, a_prio, a_category))
        self.print_list()

    def remove_activity(self):

        '''
        Manages user interactions when the remove activity option is selected. Calls ActivityList remove_from_list() method

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''

        # Check if there is an activity to remove
        if len(self.a_list) < 1:
            print("\nYour list is empty. Please add an activity first.\n")
            return
        self.print_list()

        remove_prio = 0

        # Ask user for activity to remove, check for valid user input, and then remove the activity from the activity list
        while remove_prio < 1:
            remove_prio = input(f"\nWhich activity would you like to remove [1-{len(self.a_list)}]?\n")
            remove_prio = self.check_in_range(remove_prio, len(self.a_list))
        self.a_list.remove_from_list(remove_prio)
        self.print_list()

    def change_priority(self):

        '''
        Manages user interactions when the change priority option is selected. Calls ActivityList change_list_priority() method

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''

        # Check if there is an activity to change priority for
        if len(self.a_list) < 1:
            print("\nYour list is empty. Please add an activity first.\n")
            return

        if len(self.a_list) < 2:
            print("\nYour list only has one activity. Priority cannot be changed.\n")
            return
        self.print_list()

        change_prio = new_prio = 0

        # Ask user for activity to change priority, check for valid user input, and then change the activity priority
        while change_prio < 1:
            change_prio = input(f"\nWhich activity priority would you like to change [1-{len(self.a_list)}]?\n")
            change_prio = self.check_in_range(change_prio, len(self.a_list))

        while new_prio < 1:
            new_prio = input(f'\nWhat should be the new priority for "{self.a_list.list[change_prio-1].name}" [1-{len(self.a_list)}]?\n')
            new_prio = self.check_in_range(new_prio, len(self.a_list))

        if change_prio == new_prio:
            print(f'\n"{self.a_list.list[change_prio-1].name}" already has priority {new_prio}. No changes made.\n')
            return

        self.a_list.change_list_priority(change_prio, new_prio)
        self.print_list()

    def search_yelp(self, sort):

        '''
        Manages user interactions when the search Yelp option is selected. Calls YelpAPIHandler API_call() method

        Parameters
        ----------
        sort (int):
            The sort type when conducting the Yelp search

        Returns
        -------
        A dictionary of Yelp API responses associated by business category type
        '''

        self.address = input("\nEnter a location to begin your search from. This can be a city or an address:\n")
        radius = 0

        # Check valid input for search radius
        while radius not in [5, 10, 15, 20]:
            radius = input("\nEnter a suggested search radius in miles [5, 10, 15, 20]:\n")
            try:
                radius = int(radius)
                if radius not in [5, 10, 15, 20]:
                    raise Exception
            except:
                print("Please enter a suggested search radius of 5, 10, 15, or 20.\n")

        # Convert miles to meters
        radius *= 1609

        # Fun message while API calls are executed...
        print("\nConducting some Yelp magic \u2728\u2728\u2728...\n")

        # Search by most reviews
        if sort == 1:
            sort = 'review_count'

        # Search by highest ratings
        elif sort == 2:
            sort = 'rating'

        # Search by closest distances
        elif sort == 3:
            sort = 'distance'

        # Create a YelpAPIHandler object to handle all the calls to YelpAPI
        handler = YelpAPIHandler(config.yelp_api_key, self.address, radius)
        handler.API_call(self.a_list.list, sort)

        # If no businesses were returned, print an error and return -1
        if len(handler.responses) < 1:
            print("404 Error... Yelp search returned no results for your list :(.")
            return None

        return handler.responses

    def print_yelp_output(self, sort):

        '''
        Print the results from the Yelp search

        Parameters
        ----------
        sort (int):
            The sort type when conducting the Yelp search

        Returns
        -------
        None
        '''

        # Create lists representing each column of the output table
        activity_names = ["Activity"]
        business_names = ["Business Name"]
        business_categories = ["Business Category"]
        sort_type_values = []
        locations = ["Address"]

        # Create the table string to append the output
        table = "Your search returned the following results:\n\n"

        for a in self.a_list.list:

            # If the Yelp search did not return any associated businesses, remove the activity from the output
            if a.business is None:
                print(f'Your search for "{a.name}" did not return any results. Removing it from your list.\n')
                continue

            activity_names.append(a.name)
            business_names.append(a.business.name)
            business_categories.append(a.category.title)

            # Assign a readable column name for the sort types
            if sort == 1:
                sort_type_values.append(a.business.num_reviews)
                sort_type = 'Number of Reviews'

            elif sort == 2:
                sort_type_values.append(a.business.rating)
                sort_type = 'Rating'

            elif sort == 3:
                sort_type_values.append(round(a.business.distance/1609,2))
                sort_type = 'Distance Away (miles)'

            # Create the address string
            locations.append(', '.join(a.business.location))

        sort_type_values.insert(0, sort_type)
        
        # Create rows of table
        for i in range(0, len(activity_names)):
            if i == 0:
                table += '|' + activity_names[i].center(len(max(activity_names, key=len)) + 4) + '|'
                table += business_names[i].center(len(max(business_names, key=len)) + 4) + '|'
                table += business_categories[i].center(len(max(business_categories, key=len)) + 4) + '|'
                table += sort_type_values[i].center(len(sort_type_values[0]) + 4) + '|'
                table += locations[i].center(len(max(locations, key=len)) + 4) + '|' + '\n'
                table += '-' * (len(max(activity_names, key=len)) + len(max(business_names, key=len)) + len(max(business_categories, key=len)) + len(sort_type_values[0]) + len(max(locations, key=len)) + 26) + '\n'

            else:
                table += '| ' + activity_names[i].ljust(len(max(activity_names, key=len)) + 3) + '| '
                table += business_names[i].ljust(len(max(business_names, key=len)) + 3) + '| '
                table += business_categories[i].ljust(len(max(business_categories, key=len)) + 3) + '|'
                table += str(sort_type_values[i]).rjust(len(sort_type_values[0]) + 3) + ' | '
                table += locations[i].ljust(len(max(locations, key=len)) + 3) + '|' + '\n'

        print(table)

    def open_map(self):

        '''
        Opens a Google Maps web page with directions from the search address to the businesses in order of priority. Calls methods from the Map object

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''

        # Check for valid user input
        choice = ''
        while choice.lower() not in ['y','n','yes','no']:
            choice = input("\nWould you also like a map of directions to your activities [y/n]?\n")
            if choice.lower() not in ['y','n','yes','no']:
                print("\nPlease enter a valid response.\n")

        if choice in ['n', 'no']:
            return

        # Can specify the mode of travel (drive, walk, bike, transit). Currently not implemented
        # travel_mode = ''

        # Assign the search address as the origin
        directions = Map(self.address)

        # For each activity with an associated business, add them as a waypoint
        for a in self.a_list.list:

            if a.business is None:
                continue

            name_and_address = a.business.name + ', ' + ', '.join(a.business.location)
            directions.add_waypoint(name_and_address)

        directions.search_directions()

    def print_list(self):

        '''
        Print the current activity list

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''

        print(self.a_list)

    def check_in_range(self, num, max_num):

        '''
        Check if a value is a valid integer in the given range

        Parameters
        ----------
        num (str):
            Value to be checked and converted to an integer
        max_num (int):
            The max value that the integer num can take

        Returns
        -------
        The input value converted to an int OR 0 if the input value is not a valid integer
        '''

        try:
            num = int(num)
            if num < 1 or num > max_num:
                raise Exception
            return num
        except:
            print(f"\nPlease enter an integer between 1 and {max_num}.\n")
            return 0

class Activity():

    '''
    A class to store activity information.

    Attributes
    ----------
    name (str):
        The name of the activity
    prio (int):
        The priority of the activity
    category (Category):
        A Category object representing a business category
    business (YelpBusiness):
        The YelpBusiness object associated with the activity
    '''
    
    def __init__(self, name, prio, category):

        '''
        Constructs the YelpBusiness object

        Parameters
        ----------
        name (str):
            The name of the activity
        prio (int):
            The priority of the activity
        category (Category):
            A Category object representing a business category

        Returns
        -------
        None
        '''

        self.name = name
        self.prio = prio
        self.category = category
        self.business = None    

    def __repr__(self):
        string = f"{self.prio}. {self.name} [{self.category}]"
        return string

class ActivityList():

    '''
     A class to store an activity list consisting of Activity objects.

    Attributes
    ----------
    list (Activity[]):
        The list of Activity objects
    '''
    
    def __init__(self):

        '''
        Constructs the ActivityList object

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''

        self.list = []

    def __str__(self):
        string = '\nCurrent list:\n'
        for a in self.list:
            string += str(a) + '\n'
        return string

    def __len__(self):
        return len(self.list)

    def add_to_list(self, activity):

        '''
        Adds an activity to the activity list and updates the list prioritization.

        Parameters
        ----------
        activity (Activity): 
            The Activity object to be added to the list

        Returns
        -------
        None
        '''

        for a in self.list[activity.prio - 1:]:
            a.prio += 1
        self.list.insert(activity.prio - 1, activity)

    def remove_from_list(self, prio):

        '''
        Removes an activity from the activity list and updates the list prioritization.

        Parameters
        ----------
        prio (int): 
            The priority (index + 1) of the Activity object to be removed from list

        Returns
        -------
        The Activity object that was removed. 
        '''

        for a in self.list[prio:]:
            a.prio -= 1
        return self.list.pop(prio-1)

    def change_list_priority(self, prio_to_be_changed, new_prio):

        '''
        Changes the priority of an activity and updates the list prioritization. Leverages the remove_from_list and add_to_list methods.

        Parameters
        ----------
        prio_to_be_changed (int): 
            The priority (index + 1) of the Activity object to be updated
        new_prio (int):
            The new priority (index + 1) of the Activity object

        Returns
        -------
        None
        '''

        change_activity = self.remove_from_list(prio_to_be_changed)
        change_activity.prio = new_prio
        self.add_to_list(change_activity)

class YelpBusiness():

    '''
    A class to store Yelp business information.

    Attributes
    ----------
    name (str):
        The name of the business
    category (Category):
        A Category object representing a business category
    rating (float):
        The average rating of the business
    num_reviews (int):
        The number of Yelp reviews of the business
    url (str):
        The Yelp URL of the business
    coordinates (str:float{}):
        The latitude and longitude coordinates
    location (str[]):
        A list containing each line of the address
    distance (int):
        The distance from the original search location in meters
    '''

    def __init__(self, name, category, rating, num_reviews, url, coordinates, location, distance):

        '''
        Constructs the YelpBusiness object

        Parameters
        ----------
        name (str):
            The name of the business
        category (Category):
            A Category object representing a business category
        rating (float):
            The average rating of the business
        num_reviews (int):
            The number of Yelp reviews of the business
        url (str):
            The Yelp URL of the business
        coordinates (str:float{}):
            The latitude and longitude coordinates
        location (str[]):
            A list containing each line of the address
        distance (int):
            The distance from the original search location in meters

        Returns
        -------
        None
        '''

        self.name = name
        self.category = category
        self.rating = rating
        self.num_reviews = num_reviews
        self.url = url
        self.coordinates = coordinates 
        self.location = location 
        self.distance = distance 

    def __repr__(self):
        return self.name

class YelpBusinessList():

    '''
    A class to store all YelpBusiness objects of a certain business category.

    Attributes
    ----------
    business_list (YelpBusiness[]):
        The list of YelpBusiness objects
    category (Category):
        A Category object representing a business category
    sort_type (str):
        The sort type that was used to search the Yelp database
    '''
    
    def __init__(self, category, sort_type):

        '''
        Constructs the YelpBusinessList object

        Parameters
        ----------
        category (Category):
            A Category object representing a business category
        sort_type (str):
            The sort type that was used to search the Yelp database

        Returns
        -------
        None
        '''

        self.business_list = []
        self.category = category
        self.sort_type = sort_type
        
        # Change 'review_count' to 'number of reviews' for printing purposes
        if self.sort_type == 'review_count':
            self.sort_type = 'number of reviews'

    def __repr__(self):
        string = f'\nCurrent {self.category.title} List (sorted by {self.sort_type}):\n'
        for b in self.business_list:
            string += str(b) + '\n'
        return string

    def add_business(self, business):

        '''
        Adds a business to the business list.

        Parameters
        ----------
        business (YelpBusiness): 
            The YelpBusiness object to be added to business_list

        Returns
        -------
        None
        '''

        self.business_list.append(business)

    def remove_business(self, index):

        '''
        Removes a business from the business list.

        Parameters
        ----------
        index (int): 
            The index of the YelpBusiness object to be removed from business_list

        Returns
        -------
        The YelpBusiness object that was removed OR if list is empty, None
        '''

        if len(self.business_list) < 1:
            return None
        else:
            return self.business_list.pop(index)

class YelpAPIHandler():

    '''
    A class to create an object to handle YelpAPI calls.

    Attributes
    ----------
    key (str):
        YelpAPI key
    address (str):
        The search address
    radius (int):
        The search radius in meters
    responses (str:YelpBusinessList{})
        A dictionary containing the alias of categories and the associated list of businesses
    '''

    def __init__(self, key, address='', radius=0):

        '''
        Constructs the YelpAPIHandler object

        Parameters
        ----------
        key (str):
            YelpAPI key
        address (str):
            The search address
        radius (int):
            The search radius in meters

        Returns
        -------
        None
        '''

        self.yelp_api = YelpAPI(key)
        self.address = address
        self.radius = radius
        self.responses = {}

    def API_call(self, activity_list, sort):

        '''
        Makes calls to the YelpAPI for each activity in the activity_list

        Parameters
        ----------
        activity_list (Activity[]): 
            A list of activities
        sort (str): 
            The sort type when searching the Yelp database

        Returns
        -------
        None
        '''

        # A set that ensures duplicate categories aren't searched 
        check_dup_cats = set() 

        for a in activity_list:

            # Skip the YelpAPI call if the category was already search (for duplicate categories in the activity list)
            if a.category.alias not in check_dup_cats:
                check_dup_cats.add(a.category.alias)

                # Use YelpAPI call to return list of businesses and create a YelpBusinessList object
                response = self.yelp_api.search_query(location=self.address, categories=a.category.alias, radius=self.radius, sort_by=sort, limit=10)

                b_list = YelpBusinessList(a.category, sort)

                # For each business in the business list, create a YelpBusiness object
                for b in response['businesses']:
                    b_list.add_business(YelpBusiness(name=b['name'], category=a.category, rating=b['rating'], num_reviews=b['review_count'], url=b['url'], coordinates=b['coordinates'], location=b['location']['display_address'], distance=b['distance']))

                # If the response returned businesses, add it to the responses list. Else, do nothing. 
                if len(b_list.business_list) == 0:
                    pass
                else:
                    self.responses[a.category.alias] = b_list
            
            # Assign the first business in the category to the activity
            if a.category.alias in self.responses.keys():
                a.business = self.responses[a.category.alias].remove_business(0)

if __name__ == "__main__":
    start = UI("categories.json")
    start.user_input()
