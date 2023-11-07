from app.utilities import synechron_logger
from app.utilities.constants import fetch_constant
from app.utilities.db_utils.interface.db_interface import DBUtils
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
import traceback
import sys
from typing import List, Tuple, Union

logger = synechron_logger.SyneLogger(
    synechron_logger.get_logger(__name__), {"model-inference": "v1"}
)


class SynechronDbutil(DBUtils):
    """DBUtil implementation class for Synechron DB db.
    author: Rajesh
    Args:
        DBUtils (Class): Interface for all the db_util implementation.
    """

    def __init__(self) -> None:
        """Constructor to create a connection with the Synechron db.
        author: Rajesh
        """
        super(SynechronDbutil, self).__init__()
        self.connection_string = "mongodb://localhost:27017" #os.environ.get("KELSY_DB_CONN")
        self.db_name = "Synechron"
        self.max_pool = fetch_constant("max_pool")
        logger.info(
            "Initializing connection pool for database connection, should happen only"
            " once during startup. with {}".format(self.db_name)
        )

        self.DEFAULT_CONNECTION_URL = "mongodb://localhost:27017/"
        try:
            self.client = MongoClient(self.DEFAULT_CONNECTION_URL)
            self.DB_NAME = "Synechron"
            self.dataBase = self.client[self.DB_NAME]
            self.COLLECTION_NAME = "signature_verification"
            self.collection = self.dataBase[self.COLLECTION_NAME]



        except (ConnectionFailure, ServerSelectionTimeoutError):
            logger.error(
                f"Could not Connect with databse={self.db_name}. Please check the"
                " connection string",
                exc_info=True,
            )
            sys.exit(0)

    def insert_one(self, data):
        """Function to insert one item in a collection.
        Author: Rajesh
        Args:
            collection_name (str): _description_
            data (dict): _description_
        Returns:
            _id: ID of inserted document.
        """

        insert_result = self.collection.insert_one(data)
        return insert_result.inserted_id

    def insert_many(self):
        pass

    def update(self, collection_name: str, query: dict, data: dict):
        session = self.client.start_session(causal_consistency=True)
        session.start_transaction()
        try:
            self.database[collection_name].update_one(
                query, {"$set": data}, session=session
            )
            session.commit_transaction()
            logger.info(f"Updated data in {collection_name} || query = {query}")
        except Exception as exe:
            logger.error(
                f"Error in Updating the collection name="
                f" {collection_name} || query ={query} || {exe}, starting rollback.",
                exc_info=True,
            )
            session.abort_transaction()
        finally:
            session.end_session()

    def read(self,query: dict,sort: Union[List[Tuple], None] = None,col_names: Union[List[str], None] = None,max_count: int = None):
        """Function to read data from the db.
        author: Rajesh
        Args:
            collection_name (str): _description_
            query (dict): _description_
            sort (Union[List[Tuple],None], optional): _description_. Defaults to None.
            col_names (Union[List[str],None], optional): _description_. Defaults to None.
            max_count (int, optional): _description_. Defaults to None.
        Returns:
            _type_: _description_
        """
        data = self.collection.find_one(query)

        # data = []
        # session = self.client.start_session(causal_consistency=True)
        # session.start_transaction()
        # try:
        #     logger.info(f"Fetching documents from {collection_name} || query = {query}")
        #     if max_count:
        #         resp = (
        #             self.database[collection_name]
        #             .find(
        #                 filter=query, projection=col_names, session=session, sort=sort
        #             )
        #             .limit(max_count)
        #         )
        #     else:
        #         resp = self.database[collection_name].find(
        #             filter=query, projection=col_names, session=session, sort=sort
        #         )
        #     session.commit_transaction()
        #     for item in resp:
        #         data.append(item)
        # except Exception as exe:
        #     logger.error(
        #         f"Error in executing the query = {query} for collection name ="
        #         f" {collection_name} || {exe}, starting rollback.",
        #         exc_info=True,
        #     )
        #     session.abort_transaction()
        # finally:
        #     session.end_session()
        return data

    def delete(self, collection_name, query):
        session = self.client.start_session(causal_consistency=True)
        session.start_transaction()
        try:
            self.database[collection_name].delete_one(query, session=session)
            session.commit_transaction()
            logger.info(f"Removed data from {collection_name} || query = {query}")
        except Exception as exe:
            logger.error(
                f"Could not perform insertion on {collection_name} collection || {exe}",
                exc_info=True,
            )
            session.abort_transaction()
        finally:
            session.end_session()

    def get_all_collections(self):
        all_collections = []
        for coll in self.database.list_collection_names():
            all_collections.append(coll)
        return all_collections
