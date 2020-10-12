PSEUDOCODE

'''Print welcome message
	- welcome to the program
	- list of possible actions that can be inputted
		1. add an activity to the list OR 
		2. remove an activity from the list OR
		3. change the priority of the activity (pushes activities below it down in the list) OR
		4. search by location for (5, 10, or 20 mile radius of an address) stores using the list of activities (between 1 and 5 activities)
			- search for most reviewed stores OR
			- search for highest rated stores OR
			- search for shortest total distance 
				- in order or activities (i.e, shortest distance from inserted address to activity 1, shortest distance from activity 1 to activity 2, etc.)
'''

while len(activity_list) < 5 or not search_command:
	#print current activity list and ask for user input from list of possible actions
	if adding_activity_to_list_command:
		try:
			#error check the add activity input (max length of list should be 5, include valid activity category and optional priority (default will be last priority))
			#initiliaze the activity with empty yelp class, priority (move everything below down one), and category
			#change the priority of the other activities
			#add activity to the activity list
		except:
			#throw an error and return to beginning of the loop

	if remove_activity_from_list_command:
		try:
			#error check the remove activity input ()
			#change the priority of the other activities (move everything below up one)
			#remove the activity from the activity list
		except:
			#throw an error and return to beginning of the loop
	if change_activity_priority_command:
		try:
			#error check the change activity priority input
			#change the priority of this activity and the other activities below it
			#update the activity list
		except:
			#throw an error and return to beginning of the loop	
	if search_command:
		try:
			#error check the search command input (length of list should be between 1 and 5, radius should be 5, 10 or 20, inserted address should be valid)
			#set the search command flag
		except:
			#throw an error and return to the beginning of the looop

if search_command_flag:
	#print search options (by reviews, rating, or shortest distance)
	#use API calls to search the desired categories of yelp stores and initialize each store and the list of stores
	#search for the appropriate yelp store within the list of stores based on search option
	#return the list of stores that match the activity list categories and the searched option (also print other the two other search options groups)


