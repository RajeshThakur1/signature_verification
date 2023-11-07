from abc import abstractmethod
from app.utilities.singletone_factory import SyneSingleton


class DBUtils(metaclass=SyneSingleton):
    """This is and interface class that can be implemented to create a Singletone implementation.
    Args:
        metaclass (_type_, optional): _description_. Defaults to ZumaSingleton.
    """

    @abstractmethod
    def insert_one(self):
        pass

    @abstractmethod
    def insert_many(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def read(self):
        pass