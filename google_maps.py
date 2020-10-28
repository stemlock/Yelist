'''
This program contains the Map object that stores and manages all attributes and actions needed to search Google Maps for directions.
'''

import webbrowser
import urllib.parse

class Map():

	'''
	A class to manages the information necessary to search Google Maps for directions.

	Attributes
	----------
	origin (str):
	    The origin address of the search
	waypoints (str[]):
	    A list of waypoint addresses to search
	destination (str):
	    The destination address of the search
	travelmode (str):
	    The method of travel (drive, walk, bike, transit). Currently not implemented.
	'''

	def __init__(self, origin, waypoints = [], destination = None, travelmode = ''):
		
		'''
        Constructs the Map object

        Parameters
        ----------
        origin (str):
		    The origin address of the search
		waypoints (str[]):
		    A list of waypoint addresses to search
		destination (str):
		    The destination address of the search
		travelmode (str):
		    The method of travel (drive, walk, bike, transit). Currently not implemented.

        Returns
        -------
        None
        '''

		self.origin = origin
		self.waypoints = waypoints
		self.destination = destination

		# Currently not implemented
		# self.travelmode = travelmode

	def add_waypoint(self, wp):

		'''
        Adds a waypoint to the list of waypoints

        Parameters
        ----------
        wp (str):
        	The waypoint to be added

        Returns
        -------
        None
        '''

		if type(wp) is str and len(wp) > 1:
			self.waypoints.append(wp)
		else:
			raise Exception("Waypoint being added must be a string.")

	def remove_waypoint(self, index):

		'''
        Removes a waypoint from the list of waypoints

        Parameters
        ----------
        index (int): 
            The index of the waypoint to be removed from waypoints

        Returns
        -------
        The waypoint address that was removed OR if list is empty, None
        '''

		if len(self.waypoints) < 1:
			return
		return self.waypoints.pop(index)

	def url_encode(self, address):

		'''
        Encodes an address to be readable in a URL. Calls the urllib.parse quote_plus() method

        Parameters
        ----------
        address (str): 
            The address to be URL encoded

        Returns
        -------
        The encoded URL address
        '''

		encoded = urllib.parse.quote_plus(address)
		return encoded

	def search_directions(self):

		'''
        Puts together a URL string for Google Maps directions and opens the corresponding web page

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''

		url = 'https://www.google.com/maps/dir/?api=1&origin='
		
		# URL encode the origin address
		url += self.url_encode(self.origin)

		url += '&destination='

		# If destination has not been specified, set the last waypoint as destination 
		if self.destination is None:
			self.destination = self.remove_waypoint(-1)

		# URL encode the destination address
		url += self.url_encode(self.destination)

		url += '&waypoints='

		# Add each waypoint to the url string
		for waypoint in self.waypoints:
			url += self.url_encode(waypoint) + '%7C'

		# Turn on navigation/route preview
		url += '&dir_action=navigate'

		webbrowser.open(url)
		