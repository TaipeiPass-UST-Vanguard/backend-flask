import json
from datetime import datetime, timedelta
from helpers.custom_response import CustomResponse

from models.commodity_model import Commodity, db
from models.storage_model import StorageGroup, Storage

import jieba
import pandas as pd
from flask import Blueprint, request
from sqlalchemy.orm import joinedload

commodity_blueprint = Blueprint('commodity', __name__)


@commodity_blueprint.route('/commodity', methods=['POST'])
def post_commodity():
    """
    Create a new commodity
    ---
    tags:
      - commodity
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: CommodityInput
    responses:
      201:
        description: Commodity created
        schema:
          id: Commodity
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

    try:
        storage_group = db.session.query(StorageGroup).get(request_data['storageGroupId'])

        if not storage_group:
            return CustomResponse.not_found(message='Storage group not found', data=None)

        storage_group_dict = storage_group.to_dict()
        if storage_group_dict['available'] <= 0:
            return CustomResponse.bad_request(message='Storage group is full', data=None)

        commodity = Commodity(
            giverId=request_data['giverId'],
            receiverId=None,
            storageGroupId=request_data['storageGroupId'],
            name=request_data['name'],
            description=request_data['description'],

            category=request_data['category'],
            condition=request_data['condition'],
            status="giving",
            images=json.dumps(request_data['images']),

            expireTime=datetime.now() + timedelta(days=7),
            giveExpireTime=datetime.now() + timedelta(hours=3),
            receiveExpireTime=None
        )
        db.session.add(commodity)
        db.session.commit()

        empty_storage = [storage for storage in storage_group_dict['storages'] if not storage['commodityId']][0]
        storage = db.session.query(Storage).get(empty_storage['id'])
        storage.commodityId = commodity.id
        db.session.commit()
    except Exception as e:
        return CustomResponse.bad_request(message=str(e), data=None)

    return CustomResponse.created(message='Commodity created', data=commodity.to_dict())


@commodity_blueprint.route('/commodity/<commodity_id>', methods=['GET'])
def get_commodity(commodity_id):
    """
    Get a commodity by id
    ---
    tags:
      - commodity
    parameters:
      - in: path
        name: commodity_id
        required: true
        type: integer
    responses:
      200:
        description: Commodity found
        schema:
          id: Commodity
      404:
        description: Commodity not found
        schema:
          id: NotFound
      500:
        description: Internal server error
        schema:
          id: InternalError
    """
    commodity = db.session.query(Commodity).get(commodity_id)
    if not commodity:
        return CustomResponse.not_found(message='Commodity not found', data=None)

    return CustomResponse.ok(message='Commodity found', data=commodity.to_dict())


@commodity_blueprint.route('/commodity/<commodity_id>', methods=['PATCH'])
def patch_commodity(commodity_id):
    """
    Update a commodity by id
    ---
    tags:
      - commodity
    parameters:
      - in: path
        name: commodity_id
        required: true
        type: integer
      - in: body
        name: body
        required: true
        schema:
          id: CommodityUpdate
    responses:
      200:
        description: Commodity updated
        schema:
          id: Commodity
      404:
        description: Commodity not found
        schema:
          id: NotFound
      500:
        description: Internal server error
        schema:
          id: InternalError
    """


    request_data = request.get_json()

    commodity = db.session.query(Commodity).get(commodity_id)
    if not commodity:
        return CustomResponse.not_found(message='Commodity not found', data=None)

    if 'name' in request_data:
        commodity.name = request_data['name']

    if 'description' in request_data:
        commodity.description = request_data['description']

    if 'category' in request_data:
        commodity.category = request_data['category']

    if 'condition' in request_data:
        commodity.condition = request_data['condition']

    if 'images' in request_data:
        commodity.images = json.dumps(request_data['images'])

    if 'status' in request_data:
        commodity.status = request_data['status']
        if commodity.status == "receiving":
            commodity.receiveExpireTime = datetime.now() + timedelta(hours=3)
        if commodity.status == "finished":
            db.session.query(Storage).filter(Storage.commodityId == commodity.id).update({'commodityId': None})

    if 'receiverId' in request_data:
        commodity.receiverId = request_data['receiverId']

    db.session.commit()
    return CustomResponse.no_content(message='Commodity updated', data=commodity.to_dict())


@commodity_blueprint.route('/commodity', methods=['GET'])
def get_commodities():
    """
    Get a commodities
    ---
    tags:
      - commodity
    parameters:
      - in: query
        name: longitude
        type: float
      - in: query
        name: latitude
        type: float
      - in: query
        name: keyword
        type: string
      - in: query
        name: storageGroupId
        type: string
      - in: query
        name: status
        type: string
      - in: query
        name: giverId
        type: string
      - in: query
        name: receiverId
        type: string
    responses:
      200:
        description: Commodity found
        schema:
          id: CommodityQuery
      404:
        description: Commodity not found
        schema:
          id: NotFound
      500:
        description: Internal server error
        schema:
          id: InternalError
    """
    commodities = db.session.query(Commodity)

    if 'status' in request.args:
        commodities = commodities.filter(Commodity.status == request.args['status'])

    if 'giverId' in request.args:
        commodities = commodities.filter(Commodity.giverId == request.args['giverId'])

    if 'receiverId' in request.args:
        commodities = commodities.filter(Commodity.receiverId == request.args['receiverId'])

    if 'storageGroupId' in request.args:
        storage_group = db.session.query(StorageGroup).get(request.args['storageGroupId'])

        if not storage_group:
            return CustomResponse.not_found(message='Storage group not found', data=None)

        commodities = commodities.filter(Commodity.storageGroupId == request.args['storageGroupId']).all()
        return CustomResponse.ok(message='Commodities found', data=[commodity.to_dict() for commodity in commodities])

    if 'longitude' in request.args and 'latitude' in request.args and 'keyword' in request.args:
        longitude = float(request.args['longitude'])
        latitude = float(request.args['latitude'])

        commodities_df = pd.DataFrame([commodity.to_dict() for commodity in commodities])
        if commodities_df.empty:
            return CustomResponse.ok(message='Commodities found', data=[])

        storage_group_df = pd.DataFrame([
            storage_group.to_dict() for storage_group in db.session.query(StorageGroup)])[
            ['id', 'longitude', 'latitude']]
        storage_group_df.columns = ['storageGroupId', 'longitude', 'latitude']

        commodities_df = pd.merge(commodities_df, storage_group_df, on='storageGroupId')

        keyword_list = [
            keyword.lower() for keyword in jieba.cut_for_search(request.args['keyword']) if keyword.strip()]
        commodities_df['importance'] = (commodities_df['name'] + commodities_df['description']).apply(
            lambda x: sum([word in x.lower() for word in keyword_list]))

        commodities_df['longitude'] = (commodities_df['longitude'] - longitude) ** 2
        commodities_df['latitude'] = (commodities_df['latitude'] - latitude) ** 2
        commodities_df['distance'] = commodities_df['longitude'] + commodities_df['latitude']

        commodities_df.sort_values(by=['importance', 'distance'], ascending=[False, True], inplace=True)
        commodities_df.drop(
            columns=['importance', 'distance', 'longitude', 'latitude', 'giveExpireTime', 'receiveExpireTime'],
            inplace=True)

        return CustomResponse.ok(message='Commodities found', data=json.loads(commodities_df.to_json(orient='records')))

    return CustomResponse.ok(message='Commodities found', data=[commodity.to_dict() for commodity in commodities])
