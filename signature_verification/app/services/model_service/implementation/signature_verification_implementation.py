from app.utilities import synechron_logger
from app.services.model_service.interface.model_interface import Model
from transformers.pipelines import pipeline
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True
import torch
import datetime

# Functions to load and pre-process the images:
import skimage
from skimage.io import imread
from skimage import img_as_ubyte
from bson import ObjectId
import base64
import torch.nn.functional as F
import os
import pickle
import json
from sigver.preprocessing.normalize import (
    normalize_image, resize_image,
    crop_center, preprocess_signature)

# Functions to load the CNN model
from sigver.featurelearning.models import SigNet
import app.config as cfg

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

        state_dict_f, _, _ = torch.load(cfg.BASE_DIR + '/app/resources/signet.pth')
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

        return {"Status": f"Registered successfully","Name":name,"ID":str(inserted_id)}

    def isBase64(self,sb):
        try:
            if isinstance(sb, str):
                # If there's any unicode here, an exception will be thrown and the function will return false
                sb_bytes = bytes(sb, 'ascii')
            elif isinstance(sb, bytes):
                sb_bytes = sb
            else:
                raise ValueError("Argument must be string or bytes")
            return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
        except Exception:
            return False
    def verify_signature(self, id, base64_image):
        status = self.isBase64(base64_image)
        # Load the model
        logger.info("user inside the verify signature")
        logger.info(f"Base64 image without repair\n\n\n{base64_image}")
        base64_image = base64_image.replace('\n', '').replace('\r', '').replace(' ', '+')
        logger.info(f'repaired base64 encoded\n{base64_image}')
        status = self.isBase64(base64_image)
        query = {"_id": ObjectId(id)}
        data = syne_db_obj.read(query)
        object_name = data['name']
        signature_path = os.path.join(cfg.BASE_DIR + f"/app/{data['image_path']}")
        logger.info("error-1")
        actual_image = self.load_signature(signature_path)
        # png_data = base64.b64decode(base64_image + '=' * (-len(base64_image) % 4), validate=False)
        # png_data = base64.b64decode(base64_image)
        ########
        missing_padding = len(base64_image) % 4
        if missing_padding:
            base64_image += b'=' * (4 - missing_padding)

        png_data = base64.b64decode(base64_image)


        to_be_verified_image = img_as_ubyte(skimage.io.imread(png_data, plugin='imageio', as_gray=True))

        logger.info("PNG data converted successfully")
        with open(f"{cfg.BASE_DIR}/app/resources/signatures/raw_input_image.png", "wb") as png_file:
            png_file.write(png_data)
        logger.info("PNG file written successfully")

        logger.info("error-2")
        # to_be_verified_image = self.load_signature(f"{cfg.BASE_DIR}/app/resources/signatures/output.png")
        actual_image_normalized = 255 - normalize_image(actual_image, (952, 1360))
        # im = Image.fromarray(actual_image_normalized)
        # im.save(f"{cfg.BASE_DIR}/app/resources/signatures/actual_normalized.png")
        actual_image_resized = resize_image(actual_image_normalized, (170, 242))
        # im = Image.fromarray(actual_image_resized)
        # im.save(f"{cfg.BASE_DIR}/app/resources/signatures/actual_resized.png")
        actual_image_cropped = crop_center(actual_image_resized, (150, 220))
        # im = Image.fromarray(actual_image_cropped)
        # im.save(f"{cfg.BASE_DIR}/app/resources/signatures/actual_cropped.png")
        # im = Image.fromarray(actual_image_cropped)
        # im.save("actual.jpeg")
        to_be_verified_image_normalized = 255 - normalize_image(to_be_verified_image, (952, 1360))
        # im = Image.fromarray(to_be_verified_image_normalized)
        # im.save(f"{cfg.BASE_DIR}/app/resources/signatures/to_be_verified_normalized.png")
        to_be_verified_image_resized = resize_image(to_be_verified_image_normalized, (170, 242))
        # im = Image.fromarray(to_be_verified_image_resized)
        # im.save(f"{cfg.BASE_DIR}/app/resources/signatures/to_be_verified_resized.png")
        to_be_verified_image_cropped = crop_center(to_be_verified_image_resized, (150, 220))
        # im = Image.fromarray(to_be_verified_image_cropped)
        # im.save(f"{cfg.BASE_DIR}/app/resources/signatures/to_be_verified_cropped.png")
        actual_image_tensor = torch.tensor(actual_image_cropped).view(-1, 1, 150, 220).float().div(255)
        to_be_verified_image_tensor = torch.tensor(to_be_verified_image_cropped).view(-1, 1, 150, 220).float().div(
            255)


        with torch.no_grad():
            actual_image_feature = self.base_model_f(actual_image_tensor.to(self.device))
            to_be_verified_image_feature = self.base_model_f(to_be_verified_image_tensor.to(self.device))

        euclidean_distance = torch.norm(actual_image_feature - to_be_verified_image_feature)
        # cosine_similarity = F.cosine_similarity(actual_image_feature, to_be_verified_image_feature).item()
        lr = pickle.load(open(cfg.BASE_DIR + "/app/resources/sigver_cedar_lr_classifier.sav", "rb"))
        logger.info("classifier loaded successfully")
        label_pred = lr.predict(euclidean_distance.cpu().reshape(-1, 1))
        label_probs = lr.predict_proba(euclidean_distance.cpu().reshape(-1, 1))[0][1]
        # data = dict(name=object_name,label_pred=label_pred)
        if int(list(label_pred)[0]):
            data = {"name": object_name, "label_pred": int(list(label_pred)[0]), "probability": round(float(label_probs),2)*100}
        else:
            data = {"name": object_name, "label_pred": int(list(label_pred)[0]),
                    "probability": 100-round(float(label_probs), 2) * 100}
        logger.info(f"return object\n {data}")
        return data
