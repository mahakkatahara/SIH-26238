from app.integrations.digilocker.interface import DigiLockerAdapter


MOCK_DIGILOCKER_CATALOGUE = [
    {
        "document_type": "MOCK_ST_CERTIFICATE",
        "document_name": "ST Certificate",
    },
    {
        "document_type": "MOCK_INCOME_CERTIFICATE",
        "document_name": "Income Certificate",
    },
    {
        "document_type": "MOCK_CLASS_12_MARKSHEET",
        "document_name": "Class 12 Marksheet",
    },
    {
        "document_type": "MOCK_DOMICILE_CERTIFICATE",
        "document_name": "Domicile Certificate",
    },
]


class MockDigiLockerAdapter(DigiLockerAdapter):
    """Deterministic mock adapter providing simulated DigiLocker documents for SIH demonstration."""

    @classmethod
    def list_documents(cls, student) -> list[dict]:
        return [dict(doc) for doc in MOCK_DIGILOCKER_CATALOGUE]
