def create_plan(client, price="100.00", **overrides):
    payload = {
        "name": "Starter",
        "description": "Starter plan",
        "billing_cycle": "monthly",
        "price": price,
        "currency": "INR",
    }
    payload.update(overrides)
    response = client.post("/plans", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def create_customer(client, email="customer@example.com"):
    response = client.post(
        "/customers",
        json={"name": "Sample Customer", "email": email, "company_name": "Sample Co"},
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_subscription(client, customer_id, plan_id):
    response = client.post(
        "/subscriptions",
        json={"customer_id": customer_id, "plan_id": plan_id},
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_invoice(client, price="100.00", email="customer@example.com"):
    plan = create_plan(client, price)
    customer = create_customer(client, email)
    subscription = create_subscription(client, customer["id"], plan["id"])
    response = client.post(
        "/invoices/generate",
        json={"subscription_id": subscription["id"]},
    )
    assert response.status_code == 201, response.text
    return plan, customer, subscription, response.json()


def test_plan_price_must_be_greater_than_zero(client):
    response = client.post(
        "/plans",
        json={"name": "Free-ish", "billing_cycle": "monthly", "price": "0", "currency": "INR"},
    )
    assert response.status_code == 400
    assert "greater than 0" in response.json()["detail"]


def test_customer_email_must_be_unique_even_with_different_case(client):
    create_customer(client, "Person@example.com")
    response = client.post(
        "/customers",
        json={"name": "Second Person", "email": "PERSON@example.com"},
    )
    assert response.status_code == 409


def test_subscription_cannot_use_inactive_plan(client):
    plan = create_plan(client)
    customer = create_customer(client)
    deactivate = client.patch(f"/plans/{plan['id']}", json={"status": "inactive"})
    assert deactivate.status_code == 200

    response = client.post(
        "/subscriptions",
        json={"customer_id": customer["id"], "plan_id": plan["id"]},
    )
    assert response.status_code == 400


def test_customer_cannot_have_two_active_subscriptions_to_same_plan(client):
    plan = create_plan(client)
    customer = create_customer(client)
    create_subscription(client, customer["id"], plan["id"])

    response = client.post(
        "/subscriptions",
        json={"customer_id": customer["id"], "plan_id": plan["id"]},
    )
    assert response.status_code == 409


def test_invoice_uses_plan_price_snapshot_and_adds_ledger_entry(client):
    plan, customer, subscription, invoice = create_invoice(client, "49.99")
    assert invoice["amount_due"] == "49.99"
    assert invoice["amount_paid"] == "0.00"
    assert invoice["status"] == "issued"

    update = client.patch(f"/plans/{plan['id']}", json={"price": "79.00"})
    assert update.status_code == 200
    fetched = client.get(f"/invoices/{invoice['id']}")
    assert fetched.json()["amount_due"] == "49.99"

    ledger = client.get(f"/customers/{customer['id']}/ledger")
    assert ledger.status_code == 200
    assert len(ledger.json()) == 1
    assert ledger.json()[0]["entry_type"] == "invoice_created"
    assert ledger.json()[0]["reference_id"] == f"invoice:{invoice['id']}"


def test_successful_partial_payment_updates_invoice(client):
    _, _, _, invoice = create_invoice(client, "100.00")
    response = client.post(
        "/payments/record",
        json={
            "invoice_id": invoice["id"],
            "amount": "35.00",
            "currency": "INR",
            "status": "success",
            "provider_reference": "provider-success-1",
        },
    )
    assert response.status_code == 201, response.text
    assert response.json()["invoice"]["amount_paid"] == "35.00"
    assert response.json()["invoice"]["status"] == "partially_paid"


def test_successful_payment_cannot_exceed_remaining_balance(client):
    _, _, _, invoice = create_invoice(client, "100.00")
    response = client.post(
        "/payments/record",
        json={
            "invoice_id": invoice["id"],
            "amount": "100.01",
            "currency": "INR",
            "status": "success",
            "provider_reference": "too-large-payment",
        },
    )
    assert response.status_code == 400
    assert "remaining unpaid amount" in response.json()["detail"]


def test_failed_payment_does_not_increase_amount_paid(client):
    _, customer, _, invoice = create_invoice(client, "100.00")
    response = client.post(
        "/payments/record",
        json={
            "invoice_id": invoice["id"],
            "amount": "60.00",
            "currency": "INR",
            "status": "failed",
            "provider_reference": "provider-failure-1",
            "failure_reason": "Payment declined",
        },
    )
    assert response.status_code == 201, response.text
    assert response.json()["invoice"]["amount_paid"] == "0.00"
    assert response.json()["invoice"]["status"] == "issued"

    ledger = client.get(f"/customers/{customer['id']}/ledger").json()
    assert [entry["entry_type"] for entry in ledger] == ["invoice_created", "payment_failure"]
    assert ledger[1]["reference_id"].startswith("payment_attempt:")


def test_full_payment_moves_invoice_to_paid(client):
    _, _, _, invoice = create_invoice(client, "100.00")
    partial = client.post(
        "/payments/record",
        json={
            "invoice_id": invoice["id"],
            "amount": "60.00",
            "currency": "INR",
            "status": "success",
            "provider_reference": "partial-1",
        },
    )
    assert partial.status_code == 201
    full = client.post(
        "/payments/record",
        json={
            "invoice_id": invoice["id"],
            "amount": "40.00",
            "currency": "INR",
            "status": "success",
            "provider_reference": "remaining-1",
        },
    )
    assert full.status_code == 201, full.text
    assert full.json()["invoice"]["amount_paid"] == "100.00"
    assert full.json()["invoice"]["status"] == "paid"


def test_invoice_generation_requires_active_subscription(client):
    plan = create_plan(client)
    customer = create_customer(client)
    subscription = create_subscription(client, customer["id"], plan["id"])
    cancel = client.patch(f"/subscriptions/{subscription['id']}/cancel")
    assert cancel.status_code == 200

    response = client.post("/invoices/generate", json={"subscription_id": subscription["id"]})
    assert response.status_code == 400
