from neo4j import GraphDatabase
import pandas as pd
import logging

from neo4j.exceptions import ServiceUnavailable
from neo4j import GraphDatabase

class ConectorNeo4J:

    def __init__(self, uri, auth):
        driver = GraphDatabase.driver(uri, auth=auth)
        driver.verify_connectivity()
        self.driver = driver


    def close(self):

        self.driver.close()

    def __del__(self):
        if hasattr(self, 'driver') and self.driver:
            self.driver.close()

    def run_quey(self, queryString):
        with self.driver.session() as session:
            result = session.run(queryString)
            records = list(result) # Convert result to a list of records
            print("Size Found: {size}".format(size=len(records))) # Use len() on the list
            df = pd.DataFrame([dict(record) for record in records]) # Create DataFrame from records
            return df

    def run_quey_param(self, queryString, queryParam):
        with self.driver.session() as session:
            result = session.run(queryString, queryParam)
            records = list(result) # Convert result to a list of records
            print("Size Found: {size}".format(size=len(records))) # Use len() on the list
            df = pd.DataFrame([dict(record) for record in records]) # Create DataFrame from records
            return df

    def execute_query_with_params(self, query_string, parameters, database = "neo4j"):
        summary, _, records = self.driver.execute_query(
            query_string,
            parameters_ = parameters,
            database_ = database, # Or specify your database if different
            impersonated_user_ = None, # Or specify a user if needed
            routing_ = "WRITE"
        )
        print("Query executed. Records created: {records_created}".format(records_created=summary.counters.nodes_created))
        return records