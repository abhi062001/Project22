import json
from datetime import date, timedelta

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from order_intake import OrderIntakeService
service = OrderIntakeService()

def valid_order(**changes):
    order = {
        "orderId": "ORD-1005",
        "patientId": "PAT-505",
        "specimenId": "SP-9005",
        "specimenType": "blood",
        "priority": "urgent",
        "collectionDate": (date.today() - timedelta(days=1)).isoformat(),
        "requestedTests": ["Glucose", "CompleteBloodCount"],
        "senderNote": "ignored",
    }

    order.update(changes)
    return json.dumps(order)


def error_codes(result):
    return {(error.field, error.code) for error in result.errors}


def test_accepted_order():
    result = service.process(
        valid_order(
            specimenType="BLOOD",
            priority="UrGeNt"
        )
    )

    assert result.status == "Accepted"
    assert result.order.specimen_type == "Blood"
    assert result.order.priority == "Urgent"
    assert result.errors == []


def test_all_errors_are_returned():
    result = service.process(
        valid_order(
            orderId=" ",
            specimenType="Plasma",
            priority="Stat",
            collectionDate="2026-02-30",
            requestedTests=[],
        )
    )

    assert error_codes(result) == {
        ("orderId", "REQUIRED"),
        ("specimenType", "INVALID_VALUE"),
        ("priority", "INVALID_VALUE"),
        ("collectionDate", "INVALID_FORMAT"),
        ("requestedTests", "REQUIRED"),
    }


def test_id_length():
    result = service.process(valid_order(orderId="A" * 20))
    assert result.status == "Accepted"

    result = service.process(valid_order(orderId="A" * 21))
    assert ("orderId", "MAX_LENGTH") in error_codes(result)


def test_dates():
    result = service.process(
        valid_order(collectionDate="20-09-2026")
    )
    assert ("collectionDate", "INVALID_FORMAT") in error_codes(result)

    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    result = service.process(
        valid_order(collectionDate=tomorrow)
    )
    assert ("collectionDate", "FUTURE_DATE") in error_codes(result)


def test_requested_tests():
    result = service.process(
        valid_order(requestedTests=[])
    )
    assert ("requestedTests", "REQUIRED") in error_codes(result)

    result = service.process(
        valid_order(requestedTests=["Glucose", "glucose"])
    )
    assert ("requestedTests", "DUPLICATE") in error_codes(result)


def test_malformed_json():
    result = service.process('{"orderId":')

    assert result.status == "Rejected"
    assert len(result.errors) == 1
    assert result.errors[0].code == "MALFORMED_INPUT"