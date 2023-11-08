from app.utilities import synechron_logger
from app.services.model_service.interface.model_interface import Model
from transformers.pipelines import pipeline
from PIL import Image
import torch
import datetime

# Functions to load and pre-process the images:
from skimage.io import imread
from skimage import img_as_ubyte
from bson import ObjectId
import base64
import torch.nn.functional as F
import os
from sigver.preprocessing.normalize import (
    normalize_image, resize_image,
    crop_center, preprocess_signature)

# Functions to load the CNN model
from sigver.featurelearning.models import SigNet

# Functions for plotting:
import matplotlib.pyplot as plt
from app.utilities.db_utils.implementation.synechron_implementation import SynechronDbutil
plt.rcParams['image.cmap'] = 'Greys'

logger = synechron_logger.SyneLogger(
    synechron_logger.get_logger(__name__), {"model_inference": "v1"}
)
syne_db_obj = SynechronDbutil()
class SignatureVerification(Model):
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info('Using device: {}'.format(self.device))

        state_dict_f, _, _ = torch.load('resources/signet_f_lambda_0.95.pth')
        self.base_model_f = SigNet().to(self.device).eval()
        self.base_model_f.load_state_dict(state_dict_f)

    def initialize(self):
        pass

    def initialize_tokenizer(self):
        pass

    def initialize_model(self):
        pass

    def tokenize(self):
        pass

    def predict(self):
        pass

    def load_signature(self, path):
        """
        :author: Rajesh
        :param path: the path of the image
        :return: and return the byte array of the image
        """
        return img_as_ubyte(imread(path, as_gray=True))

    def register(self, file_path, name):
        logger.info("registering the new signature")
        logger.info(f"signature of {name} will be save in {file_path}")

        record = {
            "name": name,
            "image_path": file_path,
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow(),
            "deleted_at": None,
        }
        inserted_id = syne_db_obj.insert_one(data=record)
        logger.info(f"record data: {record}\n stored in signature_verification collection")

        return {"status": f"signature of {name} registered successfully with inserted_id: {inserted_id}"}


    def verify_signature(self,id, base64_image):
        # Load the model

        query = {"_id": ObjectId(id)}
        data = syne_db_obj.read(query)
        object_name = data['name']
        signature_path = data['image_path']
        actual_image = self.load_signature(signature_path)
        png_data = base64.b64decode(base64_image)
        with open(f"resources/signatures/output.png", "wb") as png_file:
            png_file.write(png_data)
        to_be_verified_image = self.load_signature(f"resources/signatures/output.png")
        actual_image_normalized = 255 - normalize_image(actual_image, (952, 1360))
        actual_image_resized = resize_image(actual_image_normalized, (170, 242))
        actual_image_cropped = crop_center(actual_image_resized, (150, 220))

        to_be_verified_image_normalized = 255 - normalize_image(to_be_verified_image, (952, 1360))
        to_be_verified_image_resized = resize_image(to_be_verified_image_normalized, (170, 242))
        to_be_verified_image_cropped = crop_center(to_be_verified_image_resized, (150, 220))

        actual_image_tensor = torch.tensor(actual_image_cropped).view(-1, 1, 150, 220).float().div(255)
        to_be_verified_image_tensor = torch.tensor(to_be_verified_image_cropped).view(-1, 1, 150, 220).float().div(255)

        with torch.no_grad():
            actual_image_feature = self.base_model_f(actual_image_tensor.to(self.device))
            to_be_verified_image_feature = self.base_model_f(to_be_verified_image_tensor.to(self.device))

        euclidean_distance = torch.norm(actual_image_feature - to_be_verified_image_feature).item()
        cosine_similarity = F.cosine_similarity(actual_image_feature, to_be_verified_image_feature).item()
        return {'name':object_name, 'euclidean_distance':euclidean_distance, 'cosine_similarity': cosine_similarity}