'''
This program contains the objects that take the Yelp business categories listed in the categories.json file and creates a category tree based on the category-subcategory relationships (referenced as parent-child relationships throughout the comments). 

A Category object is created for to manage each category and then mapped together in the CategoryTree object.
'''

class Category():

    '''
    A class to store Yelp categories. The nodes of a CategoryTree object.

    Attributes
    ----------
    alias (str):
        The category alias (defined by YelpAPI)
    title (str):
        The category title (defined by YelpAPI)
    parents (str[]):
        A list of aliases of the parent categories (defined by YelpAPI)
    children (Category[]):
        A list of Category objects of the children categories (defined by YelpAPI)
    '''

    def __init__(self, alias, title, parents):
        
        '''
        Constructs the Category object

        Parameters
        ----------
        alias (str):
            The category alias (defined by YelpAPI)
        title (str):
            The category title (defined by YelpAPI)
        parents (str[]):
            A list of aliases of the parent categories (defined by YelpAPI)

        Returns
        -------
        None
        '''

        self.alias = alias
        self.title = title
        self.parents = parents
        self.children = []
        
    def __repr__(self):
        return self.title

    def __lt__(self, other):
    	if self.title < other.title:
    		return True
    	else:
    		return False

    def __gt__(self,other):
    	if self.title > other.title:
    		return True
    	else:
    		return False
    
    def is_root(self):

        '''
        Checks if a category has any parent categories (i.e., is a root node)

        Parameters
        ----------
        None

        Returns
        -------
        Boolean value
        '''
        
        if self.parents:
            return False
        if not self.parents:
            return True
        
    def has_child(self):

        '''
        Checks if a category has any child categories (i.e., is an end node)

        Parameters
        ----------
        None

        Returns
        -------
        Boolean value
        '''

        if self.children:
            return True
        if not self.children:
            return False
    
    def add_child(self, child):

        '''
        Adds a category as child category

        Parameters
        ----------
        child (Category):
        	The Category object to add as a child (subcategory)

        Returns
        -------
        None
        '''

        self.children.append(child)
    
class CategoryTree():
    
    '''
    A class to store a Yelp category tree. Allows storage and traversal of categories.

    Attributes
    ----------
    nodes (str:Category{}):
        A dictionary containing category alias, Category object pairs
    print_output (dict):
        A nested dictionary structure representing the category tree
    '''
    
    def __init__(self, categories):

        '''
        Constructs the CategoryTree object

        Parameters
        ----------
        categories (dict[]):
            A list of categories stored as dictionaries

        Returns
        -------
        None
        '''

        self.nodes = {}

        # Create a Category object for each store category and add it to the CategoryTree
        for cat in categories:
            self.add_node(Category(cat['alias'], cat['title'], cat['parents']))

        # Find the children of each category, and create the tree structure
        self.create_children()
        self.print_output = self.create_tree()
        
    def __repr__(self):
        return "Category tree of size: " + str(len(self.nodes))

    def add_node(self, node):

        '''
        Adds a category to the nodes dictionary

        Parameters
        ----------
        node (Category):
        	The category to be added to nodes

        Returns
        -------
        None
        '''

        self.nodes[node.alias] = node

    def create_children(self):

        '''
        Adds the children of each category to the Category object

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''

        for cat in self.nodes.values():
            for parent in cat.parents:
                self.nodes[parent].add_child(cat)

    def traverse_tree(self, node, node_tree):

        '''
        Recursively traverses all branches of a category node

        Parameters
        ----------
        node (Category):
        	The category node to be traversed from
        node_tree (dict):
        	A nested dictionary structure representing the tree starting from the input category node

        Returns
        -------
        None
        '''

        # If the node has no child, stop traversal and asign an empty string to the node (end node)
        if not node.has_child():
            node_tree[node] = ''
            return

        # If the node has children, continue to traverse through each child node
        else:
            child_tree = {}
            for child in node.children:
                node_tree[node] = child_tree
                self.traverse_tree(child, child_tree)  
    
    def create_tree(self):

        '''
        Creates a nested dictionary representation of a category tree. Calls the traverse_tree() method

        Parameters
        ----------
        None

        Returns
        -------
        The nested dictionary representation of a category tree
        '''

        tree_output = {}
        for cat in self.nodes.values():

        	# Starting from each root node, create a category tree
            if cat.is_root():
                root_tree = {}
                self.traverse_tree(cat, root_tree)

                # Merge the root node tree to the category tree once the entire branch is found
                tree_output = {**tree_output, **root_tree} 
                
        return tree_output