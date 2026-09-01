from __future__ import annotations

import io
import json
import re

import qrcode
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from models.asset import Asset
from services import asset_service

_ACTIVE_RENTAL_STATUSES = ("active", "extended", "overdue")


class QRValidationError(ValueError):
    """Raised when scanned QR payload cannot be parsed."""


def get_qr_payload(asset: Asset) -> str:
    """Return the identifier encoded in asset QR codes (unique serial number)."""
    return asset.serial_number


def decode_qr_payload(qr_data: str) -> tuple[str | int, str]:
    """
    Parse scanned QR text into a lookup value and lookup type.

    Supports plain serial numbers (e.g. ``CAT-320-007``) and JSON payloads
  ``{"asset_id": 7}``.
    """
    trimmed = qr_data.strip()
    if not trimmed:
        raise QRValidationError("QR data is empty")

    if trimmed.startswith("{"):
        try:
            payload = json.loads(trimmed)
        except json.JSONDecodeError as exc:
            raise QRValidationError("Invalid QR JSON payload") from exc

        if not isinstance(payload, dict) or "asset_id" not in payload:
            raise QRValidationError("QR JSON payload must contain asset_id")

        asset_id = payload["asset_id"]
        if not isinstance(asset_id, int) or isinstance(asset_id, bool) or asset_id <= 0:
            raise QRValidationError("asset_id must be a positive integer")

        return asset_id, "asset_id"

    if not re.fullmatch(r"[\w\-.]+", trimmed):
        raise QRValidationError("Invalid QR identifier format")

    return trimmed, "serial"


def generate_qr_png(payload: str) -> bytes:
    """Generate a PNG QR code image for the given payload."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _format_status(value: str) -> str:
    return value.replace("_", " ").title()


def _has_active_rental(db: Session, asset_id: int) -> bool:
    from models.rental import Rental

    stmt = (
        select(Rental.rental_id)
        .where(
            Rental.asset_id == asset_id,
            Rental.actual_return.is_(None),
            Rental.rental_status.in_(_ACTIVE_RENTAL_STATUSES),
        )
        .limit(1)
    )
    return db.scalars(stmt).first() is not None


def determine_next_action(db: Session, asset: Asset) -> str:
    """Return the workflow action the frontend should invoke after a scan."""
    if _has_active_rental(db, asset.asset_id) or asset.rental_status in ("rented", "overdue"):
        return "check_in"
    return "check_out"


def lookup_asset_by_qr(db: Session, qr_data: str) -> Asset:
    """Resolve an asset from scanned QR data."""
    lookup_value, lookup_type = decode_qr_payload(qr_data)

    if lookup_type == "asset_id":
        asset = asset_service.get_asset_by_id(db, int(lookup_value))
    else:
        asset = asset_service.get_asset_by_serial_number(db, str(lookup_value))

    if asset is None:
        raise LookupError("Asset not found for scanned QR code")

    return asset


def build_scan_response(db: Session, asset: Asset) -> dict[str, object]:
    """Build the workflow scan response payload for a resolved asset."""
    stmt = (
        select(Asset)
        .options(
            joinedload(Asset.current_site),
            joinedload(Asset.current_operator),
        )
        .where(Asset.asset_id == asset.asset_id)
    )
    loaded = db.scalars(stmt).first()
    if loaded is None:
        raise LookupError("Asset not found for scanned QR code")

    return {
        "asset_id": loaded.asset_id,
        "serial_number": loaded.serial_number,
        "machine_name": loaded.machine_name,
        "status": _format_status(loaded.rental_status),
        "current_site": loaded.current_site.site_name if loaded.current_site else None,
        "current_operator": (
            loaded.current_operator.operator_name if loaded.current_operator else None
        ),
        "next_action": determine_next_action(db, loaded),
    }
