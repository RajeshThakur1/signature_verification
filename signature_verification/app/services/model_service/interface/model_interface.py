from abc import abstractmethod
from app.utilities.singletone_factory import SyneSingleton


class Model(metaclass=SyneSingleton):

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def initialize_tokenizer(self):
        pass

    @abstractmethod
    def initialize_model(self):
        pass

    @abstractmethod
    def tokenize(self):
        pass

    @abstractmethod
    def predict(self):
        pass
