from fastapi import APIRouter
from fastapi.security.api_key import APIKey
from app.routers import datamodels
from fastapi import File, UploadFile, Form
from app.utilities import synechron_logger
from app.services.model_service.implementation.nested_table_inference import NestedTableExtraction
from app.services.model_service.implementation.signature_verification_implementation import SignatureVerification
import os
import base64
import app.config as cfg

nested_table_obj = NestedTableExtraction()
nested_table_obj.initialize()
sign_verification_obj = SignatureVerification()

logger = synechron_logger.SyneLogger(
    synechron_logger.get_logger(__name__), {"model_inference": "v1"}
)

router = APIRouter(
    tags=["Inference"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def health_check():
    """Check the health of services
    author: Rajesh
    Returns:
        [json]: json object with a status code 200 if everything is working fine else 400.
    """
    return {"message": "Status = Healthy"}


@router.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...), ques: str= Form(...)):
    # Generate a unique filename to save the uploaded file
    file_path = os.path.join("uploads", file.filename)

    # Create the "uploads" directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)

    # Save the uploaded file to the server
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Return a response with the uploaded file's details
    return {"data": nested_table_obj.predict(file_path, ques)}

def isBase64(sb):
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

@router.post("/register_signature/") #UploadFile = File(...)
async def register_signature(base_b4: str= Form(...), name: str= Form(...)):
    # Generate a unique filename to save the uploaded file
    status = isBase64(base_b4)
    base64_string = base_b4
    # png_data = base64.b64decode(base64_string, '-_')
    logger.info(f"base-64 image\n\n{base64_string}")
    logger.info(f"len of base64:-\n{len(base64_string)}")
    logger.info(f"Base64 image without repair\n\n\n{base64_string}")
    base64_image = base64_string.replace('\n', '').replace('\r', '').replace(' ', '+')
    logger.info(f'repaired base64 encoded\n{base64_image}')
    missing_padding = len(base64_image) % 4
    if missing_padding:
        base64_image += '=' * (4 - missing_padding)

    png_data = base64.b64decode(base64_image)
    # png_data = base64.b64decode(base64_string)
    os.makedirs(f"{cfg.BASE_DIR}/app/resources/signatures/{name}", exist_ok=True)
    with open(f"{cfg.BASE_DIR}/app/resources/signatures/{name}/output.png", "wb") as png_file:
        png_file.write(png_data)
    file_path = os.path.join(f"resources/signatures/{name}", "output.png")
    return {"data": sign_verification_obj.register(file_path, name)}

@router.post("/verify_sign/") #UploadFile = File(...)
async def register_signature(id: str= Form(...), base64: str= Form(...)):
    # Generate a unique filename to save the uploaded file

    return sign_verification_obj.verify_signature(id, base64)
    # return {"data": sign_verification_obj.verify_signature(id, base64)}

