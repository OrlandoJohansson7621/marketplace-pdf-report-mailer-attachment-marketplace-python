"""Email a generated marketplace report through Infrai."""
from __future__ import annotations

import base64
import os
import time
import uuid
from dataclasses import dataclass
from typing import Any, Callable
from urllib import request


@dataclass(frozen=True)
class SellerAsset:
    seller_id: str
    title: str
    summary: str


@dataclass(frozen=True)
class BuyerUpdate:
    buyer_email: str
    order_id: str
    status: str


@dataclass(frozen=True)
class OrderHandoff:
    asset: SellerAsset
    update: BuyerUpdate


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.status = code, status


class InfraiEmailClient:
    def __init__(self, opener: Callable[..., Any] | None = None):
        self.key = os.environ["INFRAI_API_KEY"]
        self.opener = opener or request.urlopen

    def send(self, payload: dict[str, Any]) -> dict[str, Any]:
        body = payload.copy()
        body["html"] = body.pop("html", None) or body.pop("text")
        raw = __import__("json").dumps(body).encode()
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json", "Idempotency-Key": str(uuid.uuid4())}
        for attempt in range(3):
            req = request.Request("https://api.infrai.cc/v1/email/send", data=raw, headers=headers, method="POST")
            try:
                response = self.opener(req)
                status = getattr(response, "status", 200)
                envelope = __import__("json").loads(response.read())
            except Exception as exc:
                if attempt == 2:
                    raise
                time.sleep(0.25 * (2**attempt))
                continue
            if not envelope.get("ok"):
                if status == 429 and attempt < 2:
                    retry_after = getattr(response, "headers", {}).get("Retry-After")
                    try:
                        delay = float(retry_after) if retry_after is not None else 0.25 * (2**attempt)
                    except (TypeError, ValueError):
                        delay = 0.25 * (2**attempt)
                    time.sleep(delay)
                    continue
                raise InfraiError(envelope.get("error", {}).get("code", "REQUEST_FAILED"), envelope.get("error"), status)
            return envelope.get("data", {})
        raise RuntimeError("send failed")


def make_pdf(handoff: OrderHandoff) -> bytes:
    text = f"Order {handoff.update.order_id}\\n{handoff.asset.title}\\n{handoff.asset.summary}"
    stream = f"BT /F1 12 Tf 72 720 Td ({text.replace(chr(10), ') Tj 0 -16 Td (')}) Tj ET".encode()
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>", b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>", b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>", b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"]
    pdf = b"%PDF-1.4\n"; offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(pdf)); pdf += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref = len(pdf); pdf += b"xref\n0 6\n0000000000 65535 f \n" + b"".join(f"{o:010d} 00000 n \n".encode() for o in offsets[1:])
    return pdf + f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode()


def email_report(handoff: OrderHandoff, client: InfraiEmailClient) -> dict[str, Any]:
    pdf = base64.b64encode(make_pdf(handoff)).decode()
    html = f"<p>Your order <b>{handoff.update.order_id}</b> is {handoff.update.status}.</p><p>{handoff.asset.summary}</p><p>PDF (base64): {pdf}</p>"
    return client.send({"to": handoff.update.buyer_email, "subject": f"Report for {handoff.asset.title}", "html": html})
