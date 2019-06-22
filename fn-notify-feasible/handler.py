import asyncio
import datetime
import json
import uuid
import websockets
from websockets import ConnectionClosed


FN_CALL = 'notify-feasible-call'
RDM_URL = 'ws://www.radop.ml:8765/'
RDM_OPERATION = 'insert'
RDM_DATABASE = 'NOTIFY'
RDM_TABLE = 'feasability'
RDM_AUDIT_DATABASE = 'AUDIT'
RDM_AUDIT_TABLE = 'fn_notify_feasible'
MAX_PROBABILITY = 99.0
MIN_PROBABILITY = 50.0


def generate_rfc_time():
    time = datetime.datetime.utcnow()
    time = str(time.isoformat('T'))
    time = time.rsplit('.')[0] + 'Z'
    return time


def generate_uuid():
    return str(uuid.uuid4())


def success_message(message):
    status_code = 200
    response = {
        'status_code': status_code,
        'message': message
    }
    return response


def failure_message(message, status_code=500):
    response = {
        'status_code': status_code,
        'message': message
    }
    return response


async def send_audit_data(data):
    async with websockets.connect(
        f'{RDM_URL}{RDM_OPERATION}'
    ) as websocket:
        identifier = generate_uuid()
        time = generate_rfc_time()
        call = 'rethink-manager-call'
        payload = {
            'database': RDM_AUDIT_DATABASE,
            'table': RDM_AUDIT_TABLE,
            'data': data
        }

        package = {
            'id': identifier,
            'type': call,
            'payload': payload,
            'time': time
        }

        await websocket.send(json.dumps(package))

        try:
            message = await asyncio.wait_for(websocket.recv(), timeout=20)
            if message is None:
                raise Exception('No message was received from WS.')
            else:
                return message
        except (ConnectionRefusedError) as err:
            return err
        except ConnectionClosed as err:
            return err
        except RuntimeError as err:
            return err
        except Exception as err:
            return err


async def send_notify_data(data):
    async with websockets.connect(
        f'{RDM_URL}{RDM_OPERATION}'
    ) as websocket:
        identifier = generate_uuid()
        time = generate_rfc_time()
        call = 'rethink-manager-call'
        payload = {
            'database': RDM_DATABASE,
            'table': RDM_TABLE,
            'data': data
        }

        package = {
            'id': identifier,
            'type': call,
            'payload': payload,
            'time': time
        }

        await websocket.send(json.dumps(package))

        try:
            message = await asyncio.wait_for(websocket.recv(), timeout=20)
            if message is None:
                raise Exception('No message was received from WS.')
            else:
                return message
        except (ConnectionRefusedError) as err:
            return err
        except ConnectionClosed as err:
            return err
        except RuntimeError as err:
            return err
        except Exception as err:
            return err


def define_feasability(track_speed, read_speed, used_speed):
    used_excess_percentage = (used_speed/track_speed - 1) * 100
    read_excess_percentage = (read_speed/track_speed - 1) * 100
    difference = abs(read_excess_percentage - used_excess_percentage)

    if used_excess_percentage >= 50.0:
        feasability = MIN_PROBABILITY
        feasability += (read_excess_percentage / 3) + difference
    elif used_excess_percentage >= 20.0 and used_excess_percentage < 50:
        feasability = MIN_PROBABILITY
        feasability += (read_excess_percentage / 4) + difference
    elif used_excess_percentage > 0.0 and used_excess_percentage < 20.0:
        feasability = MIN_PROBABILITY
        feasability += (read_excess_percentage / 5) + difference
    else:
        return MIN_PROBABILITY

    if feasability > MAX_PROBABILITY:
        return MAX_PROBABILITY
    else:
        return feasability


def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    try:
        package = json.loads(req)
        package_type = package['type']
        package_payload = package['payload']
        package_id = package['id']

        if package_type != FN_CALL:
            error_msg = (f'Error!! The message header indicates other '
                         f'function call. Verify if the correct service '
                         f'was called.')
            response = failure_message(error_msg)

        track_speed = package_payload['max_allowed_speed']
        read_speed = package_payload['vehicle_speed']
        used_speed = package_payload['considered_speed']

        feasability = define_feasability(track_speed, read_speed, used_speed)

        data = {
            'infraction_id': package_id,
            'crash_feasability': feasability
        }

        loop = asyncio.get_event_loop()
        loop.run_until_complete(send_audit_data(package))
        notification = loop.run_until_complete(send_notify_data(data))
        notification = json.loads(notification)
        notification_id = notification['response_message']['generated_keys'][0]
        response = success_message(
            f'A probabilidade da infração {package_id} (ID) ter se tornado um'
            f' acidente foi de {str(round(feasability, 2))}%. A notificação '
            f'{notification_id} foi enviada!'
        )

    except (TimeoutError, ConnectionRefusedError) as err:
        response = failure_message(str(err))
        return response
    except ConnectionClosed as err:
        response = failure_message(str(err))
        return response
    except RuntimeError as err:
        response = failure_message(str(err))
        return response
    except Exception as err:
        response = failure_message(str(err))
        return response
    else:
        return response
