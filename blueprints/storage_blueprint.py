from datetime import datetime
from helpers.custom_response import CustomResponse

from models.storage_model import StorageGroup, Storage, db
from flask import Blueprint, request

storage_blueprint = Blueprint('storage', __name__)


@storage_blueprint.route('/storage_group', methods=['POST'])
def post_storage_group():
    """
    Create a new storage group
    ---
    tags:
      - storage
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: StorageGroupInput
    responses:
      201:
        description: Storage group created
        schema:
          id: StorageGroup
      400:
        description: Bad request
        schema:
          id: BadRequest
      500:
        description: Internal server error
        schema:
          id: InternalError
    """
    request_data = request.get_json()

    storage_group = StorageGroup(
        name=request_data['name'],
        longitude=request_data['longitude'],
        latitude=request_data['latitude']
    )
    db.session.add(storage_group)
    db.session.commit()

    storage_group = storage_group.to_dict()
    return CustomResponse.created(message='Storage group created', data=storage_group)


@storage_blueprint.route('/storage_group/<storage_group_id>', methods=['PATCH'])
def patch_storage_group(storage_group_id):
    """
    Patch a storage group
    ---
    tags:
      - storage
    parameters:
      - in: path
        name: storage_group_id
        required: true
        type: integer
      - in: body
        name: body
        schema:
          id: StorageGroupInput
    responses:
      200:
        description: Storage group patched
        schema:
          id: StorageGroup
      400:
        description: Bad request
        schema:
          id: BadRequest
      404:
        description: Not found
        schema:
          id: NotFound
      500:
        description: Internal server error
        schema:
          id: InternalError
    """
    storage_group = db.session.query(StorageGroup).get(storage_group_id)
    if not storage_group:
        return CustomResponse.not_found(message='Storage group not found', data=None)

    if 'name' in request.json:
        storage_group.name = request.json['name']

    if 'longitude' in request.json:
        storage_group.longitude = request.json['longitude']

    if 'latitude' in request.json:
        storage_group.latitude = request.json['latitude']

    db.session.commit()
    return CustomResponse.no_content(message='Storage group patched', data=storage_group.to_dict())


@storage_blueprint.route('/storage_group/<storage_group_id>', methods=['GET'])
def get_storage_group(storage_group_id):
    """
    Get a storage group
    ---
    tags:
      - storage
    parameters:
      - in: path
        name: storage_group_id
        required: true
        type: integer
    responses:
      200:
        description: Storage group found
        schema:
          id: StorageGroup
      404:
        description: Not found
        schema:
          id: NotFound
      500:
        description: Internal server error
        schema:
          id: InternalError
    """
    storage_group = db.session.query(StorageGroup).get(storage_group_id)
    if not storage_group:
        return CustomResponse.not_found(message='Storage group not found', data=None)

    storage_group = storage_group.to_dict()
    return CustomResponse.ok(message='Storage group found', data=storage_group)


@storage_blueprint.route('/storage_group', methods=['GET'])
def get_storage_groups():
    """
    Get all storage groups
    ---
    tags:
      - storage
    responses:
      200:
        description: Storage groups found
        schema:
          id: StorageGroup
      500:
        description: Internal server error
        schema:
          id: InternalError
    """
    storage_groups = db.session.query(StorageGroup).all()
    data = [storage_group.to_dict() for storage_group in storage_groups]
    return CustomResponse.ok(message='Storage groups found', data=data)


@storage_blueprint.route('/storage_group/<storage_group_id>', methods=['DELETE'])
def delete_storage_group(storage_group_id):
    """
    Delete a storage group
    ---
    tags:
      - storage
    parameters:
      - in: path
        name: storage_group_id
        required: true
        type: integer
    responses:
      200:
        description: Storage group deleted
        schema:
          id: StorageGroup
      404:
        description: Not found
        schema:
          id: NotFound
      500:
        description: Internal server error
        schema:
          id: InternalError
    """
    storage_group = db.session.query(StorageGroup).get(storage_group_id)
    if not storage_group:
        return CustomResponse.not_found(message='Storage group not found', data=None)

    db.session.delete(storage_group)
    db.session.commit()
    return CustomResponse.no_content(message='Storage group deleted', data=None)


@storage_blueprint.route('/storage', methods=['POST'])
def post_storage():
    """
    Create a new storage
    ---
    tags:
      - storage
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: StorageInput
    responses:
      201:
        description: Storage created
        schema:
          id: Storage
      400:
        description: Bad request
        schema:
          id: BadRequest
      500:
        description: Internal server error
        schema:
          id: InternalError
    """
    request_data = request.get_json()

    storage = Storage(
        storageGroupId=request_data['storageGroupId'],
        commodityId=None,
    )
    db.session.add(storage)
    db.session.commit()

    return CustomResponse.created(message='Storage created', data=storage.to_dict())


@storage_blueprint.route('/storage/<storage_id>', methods=['PATCH'])
def patch_storage(storage_id):
    """
    Patch a storage
    ---
    tags:
      - storage
    parameters:
      - in: path
        name: storage_id
        required: true
        type: integer
      - in: body
        name: body
        schema:
          id: StorageInput
    responses:
      200:
        description: Storage patched
        schema:
          id: Storage
      400:
        description: Bad request
        schema:
          id: BadRequest
      404:
        description: Not found
        schema:
          id: NotFound
      500:
        description: Internal server error
        schema:
          id: InternalError
    """
    storage = db.session.query(Storage).get(storage_id)
    request_data = request.get_json()
    if not storage:
        return CustomResponse.not_found(message='Storage not found', data=None)

    if 'storageGroupId' in request_data:
        storage.storageGroupId = request_data['storageGroupId']

    if 'commodityId' in request_data:
        storage.commodityId = request_data['commodityId']

    db.session.commit()
    return CustomResponse.no_content(message='Storage patched', data=storage.to_dict())


@storage_blueprint.route('/storage/<storage_id>', methods=['GET'])
def get_storage(storage_id):
    """
    Get a storage
    ---
    tags:
      - storage
    parameters:
      - in: path
        name: storage_id
        required: true
        type: integer
    responses:
      200:
        description: Storage found
        schema:
          id: Storage
      404:
        description: Not found
        schema:
          id: NotFound
      500:
        description: Internal server error
        schema:
          id: InternalError
    """
    storage = db.session.query(Storage).get(storage_id)
    if not storage:
        return CustomResponse.not_found(message='Storage not found', data=None)

    return CustomResponse.ok(message='Storage found', data=storage.to_dict())


@storage_blueprint.route('/storage', methods=['GET'])
def get_storages():
    """
    Get all storages
    ---
    tags:
      - storage
    parameters:
      - in: query
        name: storageGroupId
        type: integer
    responses:
      200:
        description: Storages found
        schema:
          id: Storage
      500:
        description: Internal server error
        schema:
          id: InternalError
    """
    storages = db.session.query(Storage)

    if 'storageGroupId' in request.args:
        storages = storages.filter(Storage.storageGroupId == request.args['storageGroupId'])

    data = [storage.to_dict() for storage in storages.all()]
    return CustomResponse.ok(message='Storages found', data=data)


@storage_blueprint.route('/storage/<storage_id>', methods=['DELETE'])
def delete_storage(storage_id):
    """
    Delete a storage
    ---
    tags:
      - storage
    parameters:
      - in: path
        name: storage_id
        required: true
        type: integer
    responses:
      200:
        description: Storage deleted
        schema:
          id: Storage
      404:
        description: Not found
        schema:
          id: NotFound
      500:
        description: Internal server error
        schema:
          id: InternalError
    """
    storage = db.session.query(Storage).get(storage_id)
    if not storage:
        return CustomResponse.not_found(message='Storage not found', data=None)

    db.session.delete(storage)
    db.session.commit()
    return CustomResponse.no_content(message='Storage deleted', data=None)
