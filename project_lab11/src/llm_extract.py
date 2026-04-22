from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from json_schema import ISSUE_ENUM, SERVICE_ENUM, get_extraction_schema

MONTH_PATTERN = r"(?:січня|лютого|березня|квітня|травня|червня|липня|серпня|вересня|жовтня|листопада|грудня)"


@dataclass
class ExtractConfig:
    provider: str = "auto"
    model: str = "gpt-4.1-mini"
    temperature: float = 0.2
    max_output_tokens: int = 500
    fallback_provider: str = "mock"


class LLMExtractionClient:
    def __init__(self, config: Optional[ExtractConfig] = None):
        self.config = config or ExtractConfig()
        self.schema = get_extraction_schema()
        self.active_provider = self._resolve_provider(self.config.provider)
        self.last_provider_error: Optional[str] = None

    def _resolve_provider(self, provider: str) -> str:
        if provider == "mock":
            return "mock"
        if provider == "openai":
            return "openai"
        if os.getenv("OPENAI_API_KEY"):
            return "openai"
        return "mock"

    def build_baseline_prompt(self, text: str) -> str:
        return (
            "Extract the support/admin attributes from the Ukrainian message below. "
            "Return only one JSON object with exactly these fields: "
            "primary_service, services_mentioned, issue_type, document_type, amounts_uah, date_text, location_text. "
            "Use null for missing string values and [] for missing amounts. "
            f"Allowed primary_service values: {SERVICE_ENUM}. "
            f"Allowed issue_type values: {ISSUE_ENUM}. "
            "Do not add commentary.\n\n"
            f"Text:\n{text}"
        )

    def build_repair_prompt(self, text: str, broken_output: str, validation_error: str) -> str:
        schema_json = json.dumps(self.schema, ensure_ascii=False)
        return (
            "Repair the broken extraction output so that it becomes valid JSON and passes the schema. "
            "Return only the repaired JSON object. "
            f"Schema: {schema_json}\n\n"
            f"Original text:\n{text}\n\n"
            f"Broken output:\n{broken_output}\n\n"
            f"Validation error:\n{validation_error}"
        )

    def extract(self, text: str) -> str:
        if self.active_provider == "openai":
            try:
                return self._extract_openai(text)
            except Exception as exc:
                self.last_provider_error = str(exc)
                self.active_provider = self.config.fallback_provider
        return self._extract_mock(text)

    def repair(self, text: str, broken_output: str, validation_error: str) -> str:
        if self.active_provider == "openai":
            try:
                return self._repair_openai(text, broken_output, validation_error)
            except Exception as exc:
                self.last_provider_error = str(exc)
                self.active_provider = self.config.fallback_provider
        return self._repair_mock(text, broken_output, validation_error)

    def _extract_openai(self, text: str) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        response = client.responses.create(
            model=self.config.model,
            input=self.build_baseline_prompt(text),
            temperature=self.config.temperature,
            max_output_tokens=self.config.max_output_tokens,
        )
        return response.output_text.strip()

    def _repair_openai(self, text: str, broken_output: str, validation_error: str) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        response = client.responses.create(
            model=self.config.model,
            input=self.build_repair_prompt(text, broken_output, validation_error),
            temperature=0,
            max_output_tokens=self.config.max_output_tokens,
        )
        return response.output_text.strip()

    def _extract_mock(self, text: str) -> str:
        return corrupt_json_output(heuristic_extract(text), text)

    def _repair_mock(self, text: str, broken_output: str, validation_error: str) -> str:
        return json.dumps(heuristic_extract(text), ensure_ascii=False, indent=2)


def heuristic_extract(text: str) -> Dict[str, Any]:
    lowered = normalize(text)
    services = detect_services(lowered)
    primary = services[0] if services else "unknown"
    if "євіднов" in lowered:
        primary = "єВідновлення"
    elif re.search(r"\bдія\b", lowered):
        primary = "Дія"
    elif "цнап" in lowered:
        primary = "ЦНАП"
    elif "паспорт" in lowered:
        primary = "Паспортний сервіс"
    elif "нотаріус" in lowered:
        primary = "Нотаріус"
    elif "реєстр нерухом" in lowered:
        primary = "Державний реєстр нерухомості"
    return {
        "primary_service": primary,
        "services_mentioned": services,
        "issue_type": detect_issue_type(lowered),
        "document_type": detect_document_type(lowered),
        "amounts_uah": detect_amounts(lowered),
        "date_text": detect_date(text),
        "location_text": detect_location(text),
    }


def normalize(text: str) -> str:
    return text.lower().replace("є відновлення", "євідновлення")


def detect_services(lowered: str) -> List[str]:
    found: List[str] = []
    if "євіднов" in lowered:
        found.append("єВідновлення")
    if re.search(r"\bдія\b", lowered):
        found.append("Дія")
    if "цнап" in lowered:
        found.append("ЦНАП")
    if "паспорт" in lowered:
        found.append("Паспортний сервіс")
    if "нотаріус" in lowered:
        found.append("Нотаріус")
    if "реєстр нерухом" in lowered:
        found.append("Державний реєстр нерухомості")
    if not found and any(token in lowered for token in ["повідомлення 123", "місце проживання", "прав власності"]):
        found.append("Інша держпослуга")
    seen = set()
    out: List[str] = []
    for item in found:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def detect_issue_type(lowered: str) -> str:
    if "нотаріус" in lowered or "спадщ" in lowered or "права після смерті" in lowered:
        return "inheritance_or_notary"
    if any(token in lowered for token in ["не можу", "не працювала", "не підтягуються", "немає можливості авторизуватись", "очікуйте"]):
        return "service_access_problem"
    if any(token in lowered for token in ["які документи", "який документ", "довідка", "qr - код", "qr-код", "потрібні документи", "що потрібно надати", "витяг про місце проживання", "документ"]):
        return "document_requirement"
    if any(token in lowered for token in ["оплата", "коштує", "грн", "грошової компенсації", "кошти", "виплачують"]) or bool(re.search(r"\b\d{3,6}\b", lowered)):
        return "payment_or_amount"
    if any(token in lowered for token in ["черзі", "черга", "зареєструвалася", "реєстрації", "запис", "призначеного часу"]):
        return "registration_or_queue"
    if any(token in lowered for token in ["спробуйте", "радимо", "рекомендую"]):
        return "consultation_or_advice"
    if any(token in lowered for token in ["подати заяву", "створенні заяви", "подала заяву", "подати", "внести будинок", "подаємось"]):
        return "application_submission"
    if any(token in lowered for token in ["компенсац", "відшкодування", "отримати кошти", "пошкоджене майно", "зруйноване майно"]):
        return "compensation_status"
    return "other"


def detect_document_type(lowered: str) -> Optional[str]:
    patterns = [
        ("згода другого власника", "згода другого власника"),
        ("qr - код", "QR-код"),
        ("qr-код", "QR-код"),
        ("довідка з бті", "довідка з БТІ"),
        ("витяг про місце проживання", "витяг про місце проживання"),
        ("повідомлення про пошкоджене майно", "Повідомлення про пошкоджене майно"),
        ("фото у паспорт", "фото у паспорт"),
        ("паспорт", "паспорт"),
        ("довідка", "довідка"),
        ("бланки", "бланки"),
        ("реєстр нерухомого майна", "документи для внесення нерухомості у реєстр"),
        ("заяву писали у нотаріуса", "заява у нотаріуса"),
        ("заява на отримання компенсації", "заява на компенсацію"),
    ]
    for needle, label in patterns:
        if needle in lowered:
            return label
    return None


def detect_amounts(lowered: str) -> List[float]:
    values: List[float] = []
    for match in re.findall(r"\b(\d[\d\s]{0,10})\s*(?:грн|гривень|гривні)\b", lowered):
        values.append(int(match.replace(" ", "")))
    for match in re.findall(r"\b(\d{2,3})\s*тис\b", lowered):
        values.append(int(match) * 1000)
    if "500 000" in lowered or "500000" in lowered:
        values.append(500000)
    if "200 000" in lowered or "200000" in lowered:
        values.append(200000)
    seen = set()
    out: List[float] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def detect_date(text: str) -> Optional[str]:
    patterns = [
        r"\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b",
        rf"\b\d{{1,2}}\s+{MONTH_PATTERN}(?:\s+\d{{4}})?\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(0)
    return None


def detect_location(text: str) -> Optional[str]:
    lowered = normalize(text)
    if "пл. ринок" in lowered and "льв" in lowered:
        return "пл. Ринок, м. Львова"
    if "костя левицького" in lowered:
        return "Костя Левицького"
    if "сіверьск" in lowered:
        return "Сіверьск, Донецька обл"
    if "сумської області" in lowered:
        return "Сумської області"
    if "цнап" in lowered:
        return "ЦНАП"
    return None


def corrupt_json_output(obj: Dict[str, Any], text: str) -> str:
    mode = int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16) % 6
    if mode == 0:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    if mode == 1:
        return json.dumps(obj, ensure_ascii=False)
    if mode == 2:
        return "Ось результат:\n```json\n" + json.dumps(obj, ensure_ascii=False, indent=2) + "\n```"
    if mode == 3:
        broken = dict(obj)
        broken["services_mentioned"] = ", ".join(obj["services_mentioned"])
        return json.dumps(broken, ensure_ascii=False, indent=2)
    if mode == 4:
        broken = dict(obj)
        broken.pop("issue_type", None)
        return json.dumps(broken, ensure_ascii=False, indent=2)
    return json.dumps(obj, ensure_ascii=False) + "\nP.S. перевірте вручну."
