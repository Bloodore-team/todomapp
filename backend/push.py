"""
Utilities to send Web Push notifications using pywebpush
"""
import os
import json
from pywebpush import webpush, WebPushException

VAPID_PUBLIC = os.getenv('VAPID_PUBLIC_KEY')
VAPID_PRIVATE = os.getenv('VAPID_PRIVATE_KEY')
VAPID_CLAIMS = {"sub": os.getenv('VAPID_SUB', 'mailto:admin@example.com')}


def send_push(subscription, title, body, data=None):
    payload = json.dumps({"title": title, "body": body, "data": data or {}})
    try:
        webpush(
            subscription_info={
                "endpoint": subscription.endpoint,
                "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth}
            },
            data=payload,
            vapid_private_key=VAPID_PRIVATE,
            vapid_claims=VAPID_CLAIMS
        )
        return True
    except WebPushException as ex:
        # Log the failure; consumer can remove invalid subscription if needed
        print('WebPushException', ex)
        try:
            print(ex.response.json())
        except Exception:
            pass
        return False
    except Exception as e:
        print('send_push error', e)
        return False
