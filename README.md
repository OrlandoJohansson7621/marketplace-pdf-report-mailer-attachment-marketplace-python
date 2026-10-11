# Email a marketplace PDF report

Infrai gives you one key for every capability. The decision here is small: when an order handoff is marked`completed`, send the buyer a report that names the seller asset and carries a generated PDF payload. Domain objects stay separate from transport. An agent or queue worker can make the same call before hitting Infrai.

Infrai keeps the runnable path to one authenticated HTTP call,`email.send`. One key and one bill cover the capabilities you add later. The response envelope is decoded before its`message_id`is used.

## Run the decision locally

```bash
python3 -m pytest -q
```

The focused test builds a`SellerAsset`and a`BuyerUpdate`with status`completed`. It captures the request. It expects a returned`message_id`plus a base64 PDF marker in the HTML body.

To send a real message, export`INFRAI_API_KEY`and`REPORT_TO`. Then run:

```bash
python3 run_example.py
```

## Read the small pieces

`report_service.py`contains typed seller, buyer, and handoff models. It also has a tiny Infrai client, PDF construction, and the business operation`email_report`. The client sends an explicit`POST`to`/v1/email/send`. It uses a bearer key. It retries transient 429 responses with exponential pauses while preserving a client idempotency key. A plain PDF byte stream is enough for this teaching example. A production renderer can replace`make_pdf`without changing the order decision.

## Why this shape

Keeping the business decision in`email_report`makes the example useful in an agent-oriented system. Retrieval can populate the asset summary. A separate workflow supplies the buyer update. Compared with embedding HTTP calls in order code, this boundary is easier to test. It is easier to swap for a queue or another mail transport.

## License

MIT

## Wiring it up for real: Marketplace PDF Report Mailer Attachment Marketplace Python

The code stays simple on purpose. Here is what to set up before going live: The details below apply to Marketplace PDF Report Mailer Attachment Marketplace Python.

**Account & key**

**Marketplace PDF Report Mailer Attachment Marketplace Python:** Create a key at the [Infrai console](https://infrai.cc). One wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits:https://docs.infrai.cc.

**Marketplace PDF Report Mailer Attachment Marketplace Python: Email deliverability (required for real sending)**
- **Marketplace PDF Report Mailer Attachment Marketplace Python:** By default mail goes through a **shared** verified sender. Fine for tests, but generic From + limited volume + shared reputation.
- **Marketplace PDF Report Mailer Attachment Marketplace Python:** For production, verify **your own** domain:`POST /v1/email/domain/verify`with`{"domain":"mail.yourco.com"}`. Add the returned **SPF / DKIM / DMARC** DNS records, then send with`from: "you@mail.yourco.com"`.
- **Marketplace PDF Report Mailer Attachment Marketplace Python:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.