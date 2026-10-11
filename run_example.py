import os
from report_service import BuyerUpdate, InfraiEmailClient, OrderHandoff, SellerAsset, email_report

if __name__ == "__main__":
    recipient = os.environ.get("REPORT_TO")
    if not recipient:
        raise SystemExit("Set REPORT_TO to the buyer email address")
    handoff = OrderHandoff(SellerAsset("seller-42", "Marketplace camera report", "A compact report from the seller."), BuyerUpdate(recipient, "order-1001", "completed"))
    print(email_report(handoff, InfraiEmailClient()))
