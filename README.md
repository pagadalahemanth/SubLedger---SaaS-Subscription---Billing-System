# SubLedger

SubLedger is a small billing backend built with FastAPI, SQLAlchemy, Pydantic, and SQLite. It demonstrates separated routes, services, repositories, models, schemas, configuration, and database logic. It does not contact a real payment gateway.

## Features

- Create, list, update, and deactivate plans.
- Create and list customers, and fetch customer details.
- Create (activates immediately), list, and cancel subscriptions.
- Generate invoices with a plan-price snapshot.
- Record successful and failed payment attempts.
- Update invoice balances and statuses after successful payments.
- Append invoice/payment events to a customer ledger.
- Interactive Swagger docs at `/docs`.

## Requirements

- Python 3.12 or later.
- Git (optional, for version control).
- Docker Desktop only if you prefer the container setup.

## Local setup (Windows PowerShell)

1. Open a terminal in the `SubLedger` project directory.
2. Create a virtual environment:

   ```powershell
   py -3.12 -m venv .venv
   ```

3. Activate it:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt and run `.venv\Scripts\activate.bat`, or configure your execution policy according to your organization's guidance.

4. Copy the example environment file:

   ```powershell
   Copy-Item .env.example .env
   ```

5. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. Start the API:

   ```powershell
   uvicorn app.main:app --reload
   ```

   Tables are created automatically on startup. The default SQLite file is `subledger.db` in the project directory.

7. Open Swagger at `http://127.0.0.1:8000/docs` and run the endpoints. Health check: `GET http://127.0.0.1:8000/health`.

## Local setup (macOS/Linux)

```bash
python3.12 -m venv .venv
source .venv/bin/activate
cp .env.example .env
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Docker setup

Install and start Docker Desktop, then run from the project directory:

```bash
docker compose up --build
```

Open `http://127.0.0.1:8000/docs`. Docker Compose stores the SQLite database in a named volume so data survives container restarts. To stop the service, press Ctrl+C and run `docker compose down` in another terminal. To remove the database volume as well, run `docker compose down -v` (this deletes stored data).

## Tests

```bash
pytest -q
```

The tests use a fresh in-memory SQLite database per test and do not touch the local development database.

## API list

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/plans` | Create a plan |
| GET | `/plans` | List plans |
| PATCH | `/plans/{plan_id}` | Update a plan or activate/deactivate it |
| POST | `/customers` | Create a customer |
| GET | `/customers` | List customers |
| GET | `/customers/{customer_id}` | Fetch one customer |
| POST | `/subscriptions` | Create a subscription |
| GET | `/subscriptions` | List subscriptions |
| PATCH | `/subscriptions/{subscription_id}/cancel` | Cancel a subscription |
| POST | `/invoices/generate` | Generate an invoice |
| GET | `/invoices/{invoice_id}` | Fetch an invoice |
| POST | `/payments/record` | Record a successful or failed payment attempt |
| GET | `/customers/{customer_id}/ledger` | List customer ledger events in chronological order |
| GET | `/health` | Health check |

## Important behavior

- Plan prices must be positive.
- Customer email is stored lowercase and must be unique.
- Subscriptions cannot use inactive plans, and a customer cannot have two active subscriptions to the same plan.
- Invoice amount due and currency are copied from the plan when the invoice is created. Later plan-price changes do not change old invoices.
- A successful payment cannot exceed the remaining balance. Partial success changes the invoice to `partially_paid`; full payment changes it to `paid`.
- A failed payment is recorded but does not change `amount_paid` or the invoice status.
- Ledger events are created for invoice generation, payment success, and payment failure. The application does not expose ledger update/delete operations.
- No real payment is made. The caller supplies `success` or `failed` to simulate a payment provider result.

## Assumptions and limitations

- Creating a subscription activates it immediately. No separate activation endpoint is included because the required API list only specifies create, list, and cancel.
- Billing cycles are `monthly`, `quarterly`, and `yearly`.
- Subscription periods use calendar months; `current_period_end` is the end boundary (exclusive) calculated from the start date.
- Unless provided, an invoice uses the subscription's current period and has a due date 30 days from invoice generation.
- The service is intentionally unauthenticated, matching the assignment's base scope.
- SQLite and SQLAlchemy `create_all()` keep local setup simple. `create_all()` does not migrate existing schemas after model changes; during development, reset the local database or add Alembic migrations if the project later needs schema upgrades.
- The ledger is an append-only application interface rather than a double-entry accounting system or a database-level tamper-proof audit log.
- Complex taxation, proration, billing automation, refunds, real gateways, and role-based access control are out of scope.

See [DESIGN.md](DESIGN.md) for the LLD and design decisions.
