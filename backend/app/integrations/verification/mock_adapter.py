class MockVerificationAdapter:
    """Mock verification adapter implementing conceptual verifyDocument() method for SIH demo.
    
    This is strictly a deterministic test/mock adapter.
    No live DigiLocker, APAAR, UDISE, or government APIs are called.
    """

    @classmethod
    def verify_document(cls, document) -> dict:
        doc_type = getattr(document, "document_type", None)

        if doc_type == "TEST_VERIFIED":
            return {
                "status": "VERIFIED",
                "message": "Mock document successfully verified against simulated issuer registry",
                "evaluation_mode": "MOCK",
            }
        elif doc_type == "TEST_MISMATCH":
            return {
                "status": "MISMATCH",
                "message": "Mock document attributes do not match student records (mismatch simulated)",
                "evaluation_mode": "MOCK",
            }
        elif doc_type == "TEST_FAILED":
            return {
                "status": "FAILED",
                "message": "Mock document verification failed (simulated issuer failure)",
                "evaluation_mode": "MOCK",
            }
        else:
            return {
                "status": "FAILED",
                "message": "Mock adapter has no configured verification rule for this document type",
                "evaluation_mode": "MOCK",
            }
