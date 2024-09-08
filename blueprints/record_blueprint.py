from helpers.custom_response import CustomResponse

from models.record_model import Record, db
from flask import Blueprint, request

import pandas as pd

record_blueprint = Blueprint('record', __name__)


@record_blueprint.route('/record', methods=['POST'])
def post_record():
    """
    Create a new record
    ---
    tags:
      - record
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: RecordInput
    responses:
      201:
        description: Record created
        schema:
          id: Record
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

    record = Record(
        userId=request_data['userId'],
        role=request_data['role'],
        commodityId=request_data['commodityId'],
        reward=request_data['reward'],
        reason=request_data['reason']
    )
    db.session.add(record)
    db.session.commit()

    record = record.to_dict()
    return CustomResponse.created(message='Record created', data=record)


@record_blueprint.route('/record', methods=['POST'])
def get_records():
    """
    Get all records
    ---
    tags:
      - record
    responses:
      200:
        description: Records found
        schema:
          id: RecordQuery
      500:
        description: Internal server error
        schema:
          id: InternalError
    """
    records = Record.query.all()
    records = [record.to_dict() for record in records]
    return CustomResponse.ok(message='Records found', data=records)


@record_blueprint.route('/record/<user_id>', methods=['GET'])
def get_record(user_id):
    """
    Get a record by user id
    ---
    tags:
      - record
    parameters:
      - in: path
        name: user_id
        required: true
    responses:
      200:
        description: Record found
        schema:
          id: UserRecord
      404:
        description: Record not found
        schema:
          id: NotFound
      500:
        description: Internal server error
        schema:
          id: InternalError
    """
    records = db.session.query(Record).filter(Record.userId == user_id).all()
    if not records:
        return CustomResponse.not_found(message='Record not found', data={})

    record_df = pd.DataFrame([record.to_dict() for record in records])
    recordNum = len(record_df)
    meanReward = float(record_df['reward'].mean())
    reportNum = int((record_df['reason'] == 'report').sum())
    evaluation = 'good' if reportNum < recordNum * 0.1 else 'bad'

    return CustomResponse.ok(message='Record found', data={
        'recordNum': recordNum,
        'meanReward': meanReward,
        'reportNum': reportNum,
        'evaluation': evaluation
    })