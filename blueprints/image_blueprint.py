import os
from uuid import uuid4
from pathlib import Path

from config import Config
from helpers.custom_response import CustomResponse
from models.image_model import Image, db
from flask import Blueprint, request, send_file, current_app

image_blueprint = Blueprint('image', __name__)


@image_blueprint.route('<image_id>', methods=['GET'])
def get_image(image_id):
    """
    Get image by id
    ---
    tags:
      - image
    parameters:
      - in: path
        name: id_
        required: true
        type: integer
    """
    image = Image.query.get(image_id)

    if image is None:
        return CustomResponse.not_found('image not found', {})

    return send_file(image.filepath)


@image_blueprint.route('', methods=['POST'])
def post_image():
    """
    Post image
    ---
    tags:
      - image
    parameters:
      - in: formData
        name: image
        type: file
        required: true
    responses:
      201:
        description: Image uploaded
        schema:
          id: Image
      500:
        description: Internal server error
        schema:
          id: InternalError
    """
    image = request.files['image']
    file_name = image.filename

    new_file_name = f"{uuid4()}.{file_name.split('.')[-1]}"
    new_file_path = Path(Config.IMAGE_DIR) / Path(new_file_name)
    image.save(new_file_path)

    image = Image(filename=file_name, filepath=str(new_file_path))
    db.session.add(image)
    db.session.commit()

    return CustomResponse.created('post image success', image.to_dict())


@image_blueprint.route('<image_id>', methods=['DELETE'])
def delete_image(image_id):
    """
    delete image by id
    ---
    tags:
      - image
    parameters:
      - in: path
        name: image_id
        required: true
        type: integer
    """
    attachment = Image.query.get(image_id)

    if attachment is None:
        return CustomResponse.not_found('image not found', '')

    os.remove(attachment.filepath)
    db.session.delete(attachment)
    db.session.commit()

    return CustomResponse.no_content('delete image success', attachment.to_dict())
