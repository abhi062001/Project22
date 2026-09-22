import json
from dataclasses import dataclass
from datetime import date


@dataclass
class Error:
    field: str
    code: str
    message: str


@dataclass
class Order:
    order_id: str
    patient_id: str
    specimen_id: str
    specimen_type: str
    priority: str
    collection_date: date
    requested_tests: list[str]


@dataclass
class OrderResult:
    status: str
    order: Order | None
    errors: list[Error]


class OrderIntakeService:
    def process(self, json_text: str) -> OrderResult:
        # Broken JSON / wrong top-level shape = one error.
        try:
            data = json.loads(json_text)
            if not isinstance(data, dict):
                raise ValueError()
        except (TypeError, json.JSONDecodeError, ValueError):
            return self._malformed()

        try:
            return self._validate(data)
        except ValueError:
            return self._malformed()

    def _validate(self, data):
        errors = []

        order_id = self._required_text(data, "orderId", errors)
        patient_id = self._required_text(data, "patientId", errors)
        specimen_id = self._required_text(data, "specimenId", errors)

        self._check_length("orderId", order_id, errors)
        self._check_length("patientId", patient_id, errors)
        self._check_length("specimenId", specimen_id, errors)

        specimen_type = self._choice(
            data, "specimenType",
            {"blood": "Blood", "urine": "Urine",
             "tissue": "Tissue", "saliva": "Saliva"},
            errors,
        )

        priority = self._choice(
            data, "priority",
            {"routine": "Routine", "urgent": "Urgent"},
            errors,
        )

        collection_date = self._date(data, errors)
        tests = self._tests(data, errors)

        if errors:
            return OrderResult("Rejected", None, errors)

        return OrderResult(
            "Accepted",
            Order(
                order_id,
                patient_id,
                specimen_id,
                specimen_type,
                priority,
                collection_date,
                tests,
            ),
            [],
        )

    def _required_text(self, data, field, errors):
        value = data.get(field)

        if value is None or not isinstance(value, str):
            if value is not None and not isinstance(value, str):
                raise ValueError("wrong type")
            errors.append(Error(field, "REQUIRED", f"{field} is required."))
            return ""

        if not value.strip():
            errors.append(Error(field, "REQUIRED", f"{field} is required."))

        return value

    def _check_length(self, field, value, errors):
        if value and len(value) > 20:
            errors.append(Error(field, "MAX_LENGTH", f"{field} is too long."))

    def _choice(self, data, field, choices, errors):
        value = data.get(field)

        if value is None:
            errors.append(Error(field, "REQUIRED", f"{field} is required."))
            return None

        if not isinstance(value, str):
            raise ValueError("wrong type")

        result = choices.get(value.lower())
        if result is None:
            errors.append(Error(field, "INVALID_VALUE", f"Invalid {field}."))
        return result

    def _date(self, data, errors):
        value = data.get("collectionDate")

        if value is None:
            errors.append(Error("collectionDate", "REQUIRED",
                                "collectionDate is required."))
            return None

        if not isinstance(value, str):
            raise ValueError("wrong type")

        try:
            parsed = date.fromisoformat(value)
        except ValueError:
            errors.append(Error("collectionDate", "INVALID_FORMAT",
                                "Use yyyy-MM-dd and a real date."))
            return None

        if parsed.strftime("%Y-%m-%d") != value:
            errors.append(Error("collectionDate", "INVALID_FORMAT",
                                "Use yyyy-MM-dd format."))
            return None

        if parsed > date.today():
            errors.append(Error("collectionDate", "FUTURE_DATE",
                                "Date cannot be in the future."))

        return parsed

    def _tests(self, data, errors):
        value = data.get("requestedTests")

        if value is None:
            errors.append(Error("requestedTests", "REQUIRED",
                                "requestedTests is required."))
            return []

        if not isinstance(value, list):
            raise ValueError("wrong type")

        if not value:
            errors.append(Error("requestedTests", "REQUIRED",
                                "At least one test is required."))
            return []

        if any(not isinstance(x, str) for x in value):
            raise ValueError("wrong type")

        if any(not x.strip() for x in value):
            errors.append(Error("requestedTests", "INVALID_VALUE",
                                "Test names cannot be empty."))

        names = [x.casefold() for x in value]
        if len(names) != len(set(names)):
            errors.append(Error("requestedTests", "DUPLICATE",
                                "Duplicate tests are not allowed."))

        return value

    def _malformed(self):
        return OrderResult(
            "Rejected",
            None,
            [Error("$", "MALFORMED_INPUT", "Input is not a valid order JSON.")],
        )
