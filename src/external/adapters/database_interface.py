class DatabaseInterface:
    # this is database interface
    def __init__(self):
        # initialize connection to database
        pass
    
    def findAll(self, collection_name, query=None):
        # find all data matching query from specified collection
        pass
    
    def findOne(self, collection_name, query):
        # find one data matching query from specified collection
        pass
    
    def save(self, collection_name, data):
        # save data to specified collection
        pass
    
    def insert(self, collection_name, data):
        # insert data to specified collection
        pass
    
    def update(self, collection_name, query, update_data):
        # update data in specified collection
        pass
    
    def delete(self, collection_name, query):
        # delete data from specified collection
        pass
    
    def close_connection(self):
        # close the database connection
        pass
