# Yelist

## Abstract

This program helps a user manage an activity list and then search for the applicable businesses on Yelp leveraging the Yelp Fusion API. A user can associate an activity to a particular business category in order to search for businesses that will match that activity. 

The Yelp search will be conducted based on user provided criteria, such as search address, radius, and type of search (search by most reviewed businesses, highest rated businesses, or businesses closest to search address). The program will return the results of the Yelp search in a user friendly readable table.

## Problem Statement

Yelp does not have a built-in feature to chain together searches for multiple stores and optimize store selection based on a search parameter, such as distance between stores. To cater to those who heavily rely on Yelp to search through and visit multiple stores on a single day, there is a need to have a centralized location where these stores can be stored and managed in an ordered list, and a method for optimizing which stores to visit based on several factors such as locality, store rating, or meeting user needs. 

## Tools Used

- Python
- Yelp API
- Google Maps

## Project Outcomes 

A program was designed to allow the user to create and manage a prioritized activity list based on Yelp store categories and then conduct a search via the Yelp API that returns a user catered list of stores based on the activity search criteria. The search type will dictate which Yelp stores the search algorithm will return. The search will return a single store per activity based on the Yelp store category and based on the search criteria, ordered by the priority of the activity list. Finally, the user has the option to retrieve the Google Maps directions (defaulting to driving directions) between the returned stores in order of priority.

## Technical Specifications

1. Libraries to be installed
	- YelpAPI library (“pip install yelp”)2. Imports	- `Categories.json` 	- `google_maps.py` 
	- `yelp_categories.py`3. Yelp API key
	- Imported from `config.py`, which is not included in this repository for privacy reasons 4. Using the project
	- All interactions are made via the command line (instructions provided in the interface). User input error checking is implemented throughout. Yelp search may not always use provided criteria (e.g., if the input search address is invalid, it may use a different address, or if the appropriate business cannot be found within a certain radius, it may expand the search distance). Additionally, Yelp businesses with invalid addresses may not be found when the Google Maps directions are returned.

