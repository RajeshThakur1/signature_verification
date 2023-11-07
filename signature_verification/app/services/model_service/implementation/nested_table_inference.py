from app.utilities import synechron_logger
from app.services.model_service.interface.model_interface import Model
from transformers.pipelines import pipeline
from PIL import Image

logger = synechron_logger.SyneLogger(
    synechron_logger.get_logger(__name__), {"model_inference": "v1"}
)
class NestedTableExtraction(Model):
    """This is for extraction of the nested table.
        author: Rajesh
        Args:
            Model (_type_): Interface for model
        """

    def __init__(self) -> None:
        """Constructor for LayoutLM to initilize the parameters.
        author: Rajesh
        Args:
            model_path (str): path to the model, either hugginface path or the local folder where both model and tokenizer is stored.
            thresold (float): _description_
        """
        self.model_path = "magorshunov/layoutlm-invoices"

    def initialize(self):
        """Method to initialze the model and the tokenizer.
        author: Rajesh
        """
        self.nlp = pipeline("document-question-answering", self.model_path)
        logger.info(
            f"LayoutLM model = {self.model_path} loaded on device"
        )

    def initialize_tokenizer(self):
        pass

    def initialize_model(self):
        pass

    def tokenize(self):
        pass

    def predict(self, image_path, user_question):
        """This method is used to extract the information from the LayoutLM.

                Returns:
                    dict: _description_
                """
        if image_path:
            # self.initialize()  # need to be commented
            image = Image.open(image_path)
            # nlp = pipeline("document-question-answering", self.model_path)
            answer = self.nlp(image, user_question)[0]["answer"]
            return {"user-question": user_question, "answer": answer}

        else:
            return ""
