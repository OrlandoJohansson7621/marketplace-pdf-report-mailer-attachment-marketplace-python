import json
from report_service import BuyerUpdate, InfraiEmailClient, OrderHandoff, SellerAsset, email_report


class Reply:
    status = 200
    def read(self):
        return json.dumps({"ok": True, "data": {"message_id": "m-1"}}).encode()


def test_completed_order_sends_report(monkeypatch):
    monkeypatch.setenv("INFRAI_API_KEY", "test-key")
    seen = []
    def opener(req):
        seen.append(json.loads(req.data))
        return Reply()
    handoff = OrderHandoff(SellerAsset("s-7", "Camera", "Lens and body"), BuyerUpdate("buyer@example.com", "o-9", "completed"))
    result = email_report(handoff, InfraiEmailClient(opener))
    assert result["message_id"] == "m-1"
    assert seen[0]["to"] == "buyer@example.com"
    assert "PDF (base64):" in seen[0]["html"]
