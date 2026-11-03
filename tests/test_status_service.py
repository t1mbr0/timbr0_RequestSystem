import unittest

from request_system.services.status_service import Status, can_transition


class StatusServiceTests(unittest.TestCase):
    def test_operator_starts_assigned_request(self):
        allowed, reason = can_transition(
            Status.NEW, Status.IN_PROGRESS, "operator", has_executor=True
        )
        self.assertTrue(allowed)
        self.assertEqual(reason, "allowed")

    def test_new_request_requires_executor(self):
        allowed, reason = can_transition(
            Status.NEW, Status.IN_PROGRESS, "operator", has_executor=False
        )
        self.assertFalse(allowed)
        self.assertEqual(reason, "executor_required")

    def test_executor_finishes_only_assigned_request(self):
        allowed, reason = can_transition(
            Status.IN_PROGRESS, Status.DONE, "executor", is_assigned=False
        )
        self.assertFalse(allowed)
        self.assertEqual(reason, "executor_not_assigned")

    def test_applicant_cannot_close_foreign_request(self):
        allowed, reason = can_transition(
            Status.DONE, Status.CLOSED, "applicant", is_owner=False
        )
        self.assertFalse(allowed)
        self.assertEqual(reason, "not_request_owner")

    def test_closed_request_is_immutable(self):
        allowed, reason = can_transition(
            Status.CLOSED, Status.IN_PROGRESS, "admin", has_executor=True
        )
        self.assertFalse(allowed)
        self.assertEqual(reason, "transition_forbidden")


if __name__ == "__main__":
    unittest.main()
