import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict

import keyring
import requests

OIDC_BASE_URL = os.environ.get("OIDC_BASE_URL", "https://auth.cern.ch/auth/realms/cern/protocol/openid-connect")
SSO_CLIENT_ID = os.environ.get("SSO_CLIENT_ID", "ganga-ai-prod")
BACKEND_CLIENT_ID = os.environ.get("BACKEND_CLIENT_ID", "ganga-ai-backend")
KEYRING_SERVICE = os.environ.get("KEYRING_SERVICE", "ganga-cli")
KEYRING_KEY = "exchanged_tokens"


def stderr(*args: str):
    sys.stderr.write(" ".join(map(str, args)) + "\n")
    sys.stderr.flush()


def _now():
    return datetime.now(tz=timezone.utc)


def _save(tokens: dict):
    keyring.set_password(KEYRING_SERVICE, KEYRING_KEY, json.dumps(tokens))


def _load() -> Optional[dict]:
    data = keyring.get_password(KEYRING_SERVICE, KEYRING_KEY)
    if not data:
        return None
    try:
        return json.loads(data)
    except Exception:
        return None


def _delete():
    try:
        keyring.delete_password(KEYRING_SERVICE, KEYRING_KEY)
    except Exception:
        pass


def _expired(tokens: dict) -> bool:
    ts = tokens.get("_timestamp")
    exp = tokens.get("expires_in")
    if not ts or not exp:
        return True
    try:
        t0 = datetime.fromisoformat(ts)
    except Exception:
        return True
    return _now() >= (t0 + timedelta(seconds=int(exp)) - timedelta(seconds=60))


def device_authorization_login(clientid=SSO_CLIENT_ID, scopes="openid offline_access"):
    r = requests.post(
        f"{OIDC_BASE_URL}/devicecode",
        data={"client_id": clientid, "scope": scopes},
        timeout=30,
    )
    if not r.ok:
        stderr(r.text)
        raise RuntimeError("Device authorization failed.")

    auth = r.json()
    stderr("CERN SSO Device Login\n")
    stderr("Go to:", auth.get("verification_uri") or auth.get("verification_uri_complete"))
    if "user_code" in auth:
        stderr("Enter code:", auth["user_code"])
    stderr("Waiting for login...")

    interval = int(auth.get("interval", 5))
    device_code = auth["device_code"]

    while True:
        time.sleep(interval)
        r2 = requests.post(
            f"{OIDC_BASE_URL}/token",
            data={
                "client_id": clientid,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": device_code,
            },
            timeout=30,
        )
        if r2.ok:
            return r2.json()

        try:
            err = r2.json().get("error")
        except Exception:
            err = None

        if err == "authorization_pending":
            continue
        if err == "slow_down":
            interval += 5
            continue

        raise RuntimeError(f"Device login error: {err}")


def token_exchange(subject_token: str):
    r = requests.post(
        f"{OIDC_BASE_URL}/token",
        data={
            "client_id": SSO_CLIENT_ID,
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "subject_token": subject_token,
            "audience": BACKEND_CLIENT_ID,
        },
        timeout=30,
    )
    if not r.ok:
        raise RuntimeError(f"Token exchange failed: {r.text}")
    return r.json()


def refresh_token(refresh_token: str):
    r = requests.post(
        f"{OIDC_BASE_URL}/token",
        data={"client_id": SSO_CLIENT_ID, "grant_type": "refresh_token", "refresh_token": refresh_token},
        timeout=30,
    )
    if not r.ok:
        raise RuntimeError(f"Token refresh failed: {r.text}")
    return r.json()


def perform_login() -> dict:
    initial = device_authorization_login()
    access = initial.get("access_token")
    if not access:
        raise RuntimeError("Device login did not return access token.")
    exchanged = token_exchange(access)
    exchanged["_timestamp"] = _now().isoformat()
    exchanged["_username"] = exchanged.get("sub") or ""
    _save(exchanged)
    return exchanged


def get_auth_headers() -> Dict[str, Dict[str, str]]:
    tokens = _load()
    if not tokens:
        tokens = perform_login()

    if _expired(tokens):
        rt = tokens.get("refresh_token")
        if rt:
            try:
                new = refresh_token(rt)
                new["_timestamp"] = _now().isoformat()
                new["_username"] = new.get("sub") or tokens.get("_username", "")
                _save(new)
                tokens = new
            except Exception:
                tokens = perform_login()
        else:
            tokens = perform_login()

    at = tokens.get("access_token")
    if not at:
        raise RuntimeError("Missing access token after login/refresh.")
    return {"headers": {"Authorization": f"Bearer {at}"}}


def device_logout():
    tokens = _load()
    if tokens:
        rt = tokens.get("refresh_token")
        if rt:
            try:
                requests.post(
                    f"{OIDC_BASE_URL}/revoke",
                    data={"client_id": SSO_CLIENT_ID, "token": rt, "token_type_hint": "refresh_token"},
                    timeout=10,
                )
            except Exception:
                pass
    _delete()
