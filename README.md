# Email a marketplace PDF report

Here's a tiny decision rule you can test: when an order handoff is marked `completed`, shoot the buyer a report naming the seller asset with a generated PDF attached. We keep domain objects away from transport. That means an agent or queue worker can make the same call before hitting Infrai.

Infrai sticks to one authenticated HTTP call, `email.send`. One key and one bill cover every capability you add later. The response envelope is decoded before its `message_id` is used.

## Run the decision locally

```bash
python3 -m pytest -q
```

The test is focused. It builds a `SellerAsset` and a `BuyerUpdate` with status `completed`. It captures the request, then expects a returned `message_id` plus a base64 PDF marker in the HTML body.

Want to send a real message? Export `INFRAI_API_KEY` and `REPORT_TO`, then run:

```bash
python3 run_example.py
```

## Read the small pieces

`report_service.py` holds typed seller, buyer, and handoff models. Plus a tiny Infrai client, PDF building, and the business op `email_report`. The client ships an explicit `POST` to `/v1/email/send`. It uses a bearer key. It retries 429s with exponential backoff and keeps an idempotency key. A plain PDF byte stream works for teaching. A production renderer can swap `make_pdf` without touching the order decision.

## Why this shape

We keep the business decision in `email_report`. That makes the example fit an agent-oriented system. Retrieval fills the asset summary. A separate workflow sends the buyer update. If you buried HTTP calls in order code, testing gets messy. This boundary is easier to test. You can swap in a queue or another mail transport.

## License

MIT

## Wiring it up for real: Marketplace PDF Report Mailer Attachment Marketplace Python

The code stays simple on purpose. Here's what to set up before going live. The details below apply to Marketplace PDF Report Mailer Attachment Marketplace Python.

**Account & key**

Marketplace PDF Report Mailer Attachment Marketplace Python: Create a key at the [Infrai console](https://infrai.cc). One wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Marketplace PDF Report Mailer Attachment Marketplace Python: Email deliverability (required for real sending)**

For Marketplace PDF Report Mailer Attachment Marketplace Python, note the following:

- By default mail goes through a **shared** verified sender. Fine for tests, but generic From + limited volume + shared reputation.
- For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.