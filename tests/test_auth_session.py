import unittest

from auth_session import clear_authentication, expire_inactive_session, require_admin


class SessionSecurityTests(unittest.TestCase):
    def test_active_session_is_refreshed(self):
        state = {"app_ok": True, "admin_ok": True, "auth_last_activity": 90.0}
        self.assertFalse(expire_inactive_session(state, 100.0, 30))
        self.assertEqual(state["auth_last_activity"], 100.0)
        self.assertTrue(state["admin_ok"])

    def test_inactive_session_clears_general_and_admin_access(self):
        state = {"app_ok": True, "admin_ok": True, "auth_last_activity": 10.0}
        self.assertTrue(expire_inactive_session(state, 100.0, 30))
        self.assertNotIn("app_ok", state)
        self.assertNotIn("admin_ok", state)

    def test_logout_clears_authentication_and_lockout_state(self):
        state = {
            "app_ok": True,
            "admin_ok": True,
            "app_failed_attempts": 2,
            "unrelated": "preserved",
        }
        clear_authentication(state)
        self.assertEqual(state, {"unrelated": "preserved"})

    def test_admin_boundary_rejects_unauthorised_state(self):
        with self.assertRaises(PermissionError):
            require_admin({"app_ok": True, "admin_ok": False})
        require_admin({"app_ok": True, "admin_ok": True})


if __name__ == "__main__":
    unittest.main()
