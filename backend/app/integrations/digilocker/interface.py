from abc import ABC, abstractmethod


class DigiLockerAdapter(ABC):
    @classmethod
    @abstractmethod
    def list_documents(cls, student) -> list[dict]:
        """List documents available from the provider for the specified student."""
        pass
