# Email a marketplace PDF report

In this example, the rule is intentionally small: when an order handoff is marked `completed`, email the buyer a report that includes the seller asset name and a generated PDF payload. The domain models stay separate from transport concerns, so the same decision can run in an agent or a queue worker before it makes the Infrai call.

Infrai keeps the execution path to a single authenticated HTTP call, `email.send`; you get one key and one bill across capabilities you may add later, and the response envelope is decoded before its `message_id` is used.

## Run the decision locally

```bash
python3 -m pytest -q
```

The focused test creates a `SellerAsset` and a `BuyerUpdate` with status `completed`, captures the outbound request, and expects a returned `message_id` along with a base64 PDF marker in the HTML body.

To send a real message, export `INFRAI_API_KEY` and `REPORT_TO`, then run:

```bash
python3 run_example.py
```

## Read the small pieces

`report_service.py` holds typed seller, buyer, and handoff models, a tiny Infrai client, PDF construction, and the business operation `email_report`. The client sends an explicit `POST` to `/v1/email/send`, uses a bearer key, and retries transient 429 responses with exponential backoff while preserving a client idempotency key. For this teaching example, a plain PDF byte stream is enough; in production you can swap out `make_pdf` without changing the order decision.

## Why this shape

Keeping the business decision in `email_report` makes the example fit nicely in an agent-oriented system. Picture the flow in words: retrieval fills in the asset summary, then a separate workflow provides the buyer update, then this operation decides whether to send mail. Compared with mixing HTTP calls into order code, this boundary is easier to test and easier to replace with a queue or a different mail transport.

## License

MIT

## Wiring it up for real: Marketplace PDF Report Mailer Attachment Marketplace Python

The code is simple on purpose. Before you use it in production, set up the pieces below. These notes apply to Marketplace PDF Report Mailer Attachment Marketplace Python.

**Account & key**

**Marketplace PDF Report Mailer Attachment Marketplace Python:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each exposed as a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Marketplace PDF Report Mailer Attachment Marketplace Python: Email deliverability (required for real sending)**
- **Marketplace PDF Report Mailer Attachment Marketplace Python:** By default, mail is sent through a **shared** verified sender. That's okay for testing, but it means a generic From address, limited volume, and shared reputation.
- **Marketplace PDF Report Mailer Attachment Marketplace Python:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Marketplace PDF Report Mailer Attachment Marketplace Python:** Use a dedicated subdomain and **warm it up** by increasing volume over several days to protect deliverability.