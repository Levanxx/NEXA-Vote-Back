import os
import base64
import json
from urllib.parse import urlparse
from flask import session
from app.utils.supabase_client import get_supabase_admin
from app.config import Config
from fido2.server import Fido2Server
from fido2.webauthn import (
    PublicKeyCredentialRpEntity,
    PublicKeyCredentialUserEntity,
    UserVerificationRequirement,
    CollectedClientData,
    AttestationObject,
    AuthenticatorData,
    AttestedCredentialData,
    RegistrationResponse,              
    AuthenticatorAttestationResponse,
    AuthenticationResponse,
    AuthenticatorAssertionResponse
)
from fido2 import cbor
from fido2.utils import websafe_encode, websafe_decode


def _get_server():
    origins = (os.environ.get("ALLOWED_ORIGINS") or "http://localhost:5173").split(",")
    rp_origin = origins[0].strip()
    rp_id = urlparse(rp_origin).hostname or "localhost"

    rp = PublicKeyCredentialRpEntity(id=rp_id, name="NEXA Vote")
    return Fido2Server(rp, verify_origin=lambda o: o in origins)


def register_begin(voter_id, email, full_name):
    server = _get_server()

    create_options, state = server.register_begin(
        user=PublicKeyCredentialUserEntity(
            id=voter_id.encode(),
            name=email,
            display_name=full_name,
        ),
        user_verification=UserVerificationRequirement.REQUIRED,
        authenticator_attachment="platform",
        resident_key_requirement="required",
    )

    # Guardar challenge en session (firmado con SECRET_KEY)
    return create_options, state


def register_complete(voter_id, data, state):
    server = _get_server()

    auth_data = server.register_complete(
        state,
        RegistrationResponse(
            raw_id=websafe_decode(data.get("raw_id", data["id"])),
            response=AuthenticatorAttestationResponse(
                client_data=CollectedClientData(
                    websafe_decode(data["response"]["client_data_json"])
                ),
                attestation_object=AttestationObject(
                    websafe_decode(data["response"]["attestation_object"])
                ),
            ),
        ),
    )


    cd = auth_data.credential_data
    # bytes(cd) incluye aaguid(16) + cred_id(length+value) + public_key(cbor)
    credential_raw = websafe_encode(bytes(cd))

    get_supabase_admin().table("webauthn_credentials").upsert({
        "voter_id": voter_id,
        "credential_raw": credential_raw,
        "credential_id": websafe_encode(cd.credential_id),
        "public_key": websafe_encode(cbor.encode(cd.public_key)),
        "sign_count": 0,
    }, on_conflict="voter_id").execute()




def auth_begin(voter_id):
    supabase_admin = get_supabase_admin()
    row = supabase_admin.table("webauthn_credentials") \
        .select("*") \
        .eq("voter_id", voter_id) \
        .limit(1) \
        .execute()

    if not row.data:
        raise Exception("No hay WebAuthn registrado")

    r = row.data[0]
    credential_data = AttestedCredentialData(
        websafe_decode(r["credential_raw"])
    )

    server = _get_server()
    request_options, state = server.authenticate_begin(
        credentials=[credential_data],
        user_verification=UserVerificationRequirement.REQUIRED,
    )

    return request_options, state





def auth_complete(voter_id, data, session_token_hash, state):
    supabase_admin = get_supabase_admin()
    row = supabase_admin.table("webauthn_credentials") \
        .select("*") \
        .eq("voter_id", voter_id) \
        .limit(1) \
        .execute()

    if not row.data:
        raise Exception("No hay WebAuthn registrado")

    r = row.data[0]
    credential_data = AttestedCredentialData(
        websafe_decode(r["credential_raw"])
    )

    server = _get_server()

    server.authenticate_complete(
        state,
        credentials=[credential_data],
        response=AuthenticationResponse(
            raw_id=websafe_decode(data.get("raw_id", data["id"])),
            response=AuthenticatorAssertionResponse(
                client_data=CollectedClientData(
                    websafe_decode(data["response"]["client_data_json"])
                ),
                authenticator_data=AuthenticatorData(
                    websafe_decode(data["response"]["authenticator_data"])
                ),
                signature=websafe_decode(data["response"]["signature"]),
            ),
        ),
    )

    # Marcar MFA completo
    supabase_admin.table("mfa_sessions") \
        .update({"webauthn_validated": True}) \
        .eq("voter_id", voter_id) \
        .eq("session_token_hash", session_token_hash) \
        .execute()

    return True





