import os
import subprocess
import time
import unittest
from uuid import uuid4

import requests

from app.auth.service import DATABASE_URL, SessionLocal, User, reset_refresh_sessions_for_tests, init_db as init_auth_db
from app.drafts.service import Draft, init_db as init_drafts_db
from app.research_slices.service import ResearchSlice, init_db as init_research_slices_db
from tests.db_rebind_helper import build_clean_test_env

os.environ.setdefault("AUTH_SECRET_KEY", "test-secret-research-slices")
os.environ.setdefault("COOKIE_HTTPONLY", "true")
os.environ.setdefault("COOKIE_SAMESITE", "lax")
os.environ.setdefault("APP_ENV", "development")


class ResearchSlicesApiTests(unittest.TestCase):
    SERVER_PORT = 8031
    BASE_URL = f"http://127.0.0.1:{SERVER_PORT}"

    @classmethod
    def setUpClass(cls):
        init_auth_db()
        init_drafts_db()
        init_research_slices_db()
        env = build_clean_test_env(
            {
                "APP_ENV": "development",
                "AUTH_SECRET_KEY": os.environ.get("AUTH_SECRET_KEY", "test-secret-research-slices"),
                "AUTH_DATABASE_URL": DATABASE_URL,
                "AUTH_SESSION_BACKEND": "memory",
            }
        )
        cls.server = subprocess.Popen(
            ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(cls.SERVER_PORT), "--log-level", "warning"],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        for _ in range(50):
            try:
                response = requests.get(f"{cls.BASE_URL}/api/health", timeout=0.5)
                if response.status_code == 200:
                    break
            except requests.RequestException:
                pass
            time.sleep(0.2)
        else:
            raise RuntimeError("Failed to start test server")

    @classmethod
    def tearDownClass(cls):
        cls.server.terminate()
        cls.server.wait(timeout=5)

    def setUp(self):
        init_auth_db()
        init_drafts_db()
        init_research_slices_db()
        db = SessionLocal()
        db.query(ResearchSlice).delete()
        db.query(Draft).delete()
        db.query(User).delete()
        db.commit()
        db.close()
        reset_refresh_sessions_for_tests()
        self.session = requests.Session()
        seed = uuid4().hex
        self.session.headers.update({"x-forwarded-for": f"10.{int(seed[0:2], 16)}.{int(seed[2:4], 16)}.{int(seed[4:6], 16)}"})

    def tearDown(self):
        reset_refresh_sessions_for_tests()
        self.session.close()

    def _register_login(self, email: str, password: str = "password123") -> dict[str, str]:
        register = self.session.post(
            f"{self.BASE_URL}/api/auth/register",
            json={"email": email, "password": password},
            timeout=5,
        )
        self.assertEqual(register.status_code, 201, register.text)

        login = self.session.post(
            f"{self.BASE_URL}/api/auth/login",
            json={"email": email, "password": password},
            timeout=5,
        )
        self.assertEqual(login.status_code, 200, login.text)
        token = login.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    @staticmethod
    def _payload() -> dict:
        return {
            "title": "  Test Slice  ",
            "description": "  Baseline context  ",
            "feature_refs": [{"feature_id": "recA"}, {"feature_id": "recB"}],
            "time_range": {"start": 1500, "end": 1750, "mode": "range"},
            "view_state": {
                "center": [12.4964, 41.9028],
                "zoom": 5.8,
                "enabled_layer_ids": ["renaissance_italy", "baroque_monarchies"],
                "active_quick_layer_ids": ["renaissance_italy"],
                "selected_feature_id": "recA",
            },
            "annotations": [
                {"id": "ann-1", "type": "fact", "text": "Known factual note", "feature_id": "recA"},
                {"id": "ann-2", "type": "interpretation", "text": "Interpretative note"},
                {"id": "ann-3", "type": "hypothesis", "text": "Hypothesis note"},
            ],
        }

    def test_create_get_patch_delete_research_slice_success(self):
        headers = self._register_login(f"slice-{uuid4().hex}@example.com")

        create = self.session.post(f"{self.BASE_URL}/api/research-slices", json=self._payload(), headers=headers, timeout=5)
        self.assertEqual(create.status_code, 201, create.text)
        created = create.json()
        self.assertIsInstance(created["id"], str)
        self.assertEqual(created["title"], "Test Slice")
        self.assertEqual(created["description"], "Baseline context")
        self.assertEqual(created["visibility"], "private")

        slice_id = created["id"]
        get_resp = self.session.get(f"{self.BASE_URL}/api/research-slices/{slice_id}", headers=headers, timeout=5)
        self.assertEqual(get_resp.status_code, 200, get_resp.text)
        loaded = get_resp.json()
        self.assertEqual(loaded["id"], slice_id)
        self.assertEqual(loaded["annotations"][2]["type"], "hypothesis")

        patch_resp = self.session.patch(
            f"{self.BASE_URL}/api/research-slices/{slice_id}",
            json={
                "title": "Updated",
                "description": "Updated context",
                "feature_refs": [{"feature_id": "recB"}],
                "view_state": {
                    "center": [10.0, 20.0],
                    "zoom": 7,
                    "enabled_layer_ids": ["baroque_monarchies"],
                    "active_quick_layer_ids": ["baroque_monarchies"],
                    "selected_feature_id": "recB",
                },
            },
            headers=headers,
            timeout=5,
        )
        self.assertEqual(patch_resp.status_code, 200, patch_resp.text)
        updated = patch_resp.json()
        self.assertEqual(updated["title"], "Updated")
        self.assertEqual(updated["feature_refs"], [{"feature_id": "recB"}])

        delete_resp = self.session.delete(f"{self.BASE_URL}/api/research-slices/{slice_id}", headers=headers, timeout=5)
        self.assertEqual(delete_resp.status_code, 204)

        missing = self.session.get(f"{self.BASE_URL}/api/research-slices/{slice_id}", headers=headers, timeout=5)
        self.assertEqual(missing.status_code, 404)

    def test_list_returns_only_owner_items_and_is_lightweight(self):
        headers_a = self._register_login(f"slice-a-{uuid4().hex}@example.com")
        headers_b = self._register_login(f"slice-b-{uuid4().hex}@example.com")

        create_a = self.session.post(f"{self.BASE_URL}/api/research-slices", json=self._payload(), headers=headers_a, timeout=5)
        self.assertEqual(create_a.status_code, 201)

        payload_b = self._payload()
        payload_b["title"] = "Second"
        create_b = self.session.post(f"{self.BASE_URL}/api/research-slices", json=payload_b, headers=headers_b, timeout=5)
        self.assertEqual(create_b.status_code, 201)

        listed = self.session.get(f"{self.BASE_URL}/api/research-slices", headers=headers_a, timeout=5)
        self.assertEqual(listed.status_code, 200)
        body = listed.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["title"], "Test Slice")
        self.assertIn("feature_count", body[0])
        self.assertNotIn("feature_refs", body[0])
        self.assertNotIn("description", body[0])

    def test_unauthorized_returns_401(self):
        create = self.session.post(f"{self.BASE_URL}/api/research-slices", json=self._payload(), timeout=5)
        self.assertEqual(create.status_code, 401)

        listed = self.session.get(f"{self.BASE_URL}/api/research-slices", timeout=5)
        self.assertEqual(listed.status_code, 401)

    def test_non_owner_access_is_blocked(self):
        owner_headers = self._register_login(f"slice-owner-{uuid4().hex}@example.com")
        outsider_headers = self._register_login(f"slice-outsider-{uuid4().hex}@example.com")

        create = self.session.post(f"{self.BASE_URL}/api/research-slices", json=self._payload(), headers=owner_headers, timeout=5)
        self.assertEqual(create.status_code, 201)
        slice_id = create.json()["id"]

        outsider_get = self.session.get(f"{self.BASE_URL}/api/research-slices/{slice_id}", headers=outsider_headers, timeout=5)
        self.assertEqual(outsider_get.status_code, 404)

        outsider_delete = self.session.delete(f"{self.BASE_URL}/api/research-slices/{slice_id}", headers=outsider_headers, timeout=5)
        self.assertEqual(outsider_delete.status_code, 404)

    def test_validation_errors(self):
        headers = self._register_login(f"slice-validate-{uuid4().hex}@example.com")

        invalid_title = self._payload()
        invalid_title["title"] = "   "
        response = self.session.post(f"{self.BASE_URL}/api/research-slices", json=invalid_title, headers=headers, timeout=5)
        self.assertEqual(response.status_code, 422)

        invalid_feature_refs = self._payload()
        invalid_feature_refs["feature_refs"] = []
        response = self.session.post(f"{self.BASE_URL}/api/research-slices", json=invalid_feature_refs, headers=headers, timeout=5)
        self.assertEqual(response.status_code, 422)

        invalid_annotation = self._payload()
        invalid_annotation["annotations"][0]["type"] = "unknown"
        response = self.session.post(f"{self.BASE_URL}/api/research-slices", json=invalid_annotation, headers=headers, timeout=5)
        self.assertEqual(response.status_code, 422)

        invalid_time = self._payload()
        invalid_time["time_range"] = {"start": 1800, "end": 1700, "mode": "range"}
        response = self.session.post(f"{self.BASE_URL}/api/research-slices", json=invalid_time, headers=headers, timeout=5)
        self.assertEqual(response.status_code, 422)

        invalid_center = self._payload()
        invalid_center["view_state"]["center"] = [12.0]
        response = self.session.post(f"{self.BASE_URL}/api/research-slices", json=invalid_center, headers=headers, timeout=5)
        self.assertEqual(response.status_code, 422)


        created_valid = self.session.post(f"{self.BASE_URL}/api/research-slices", json=self._payload(), headers=headers, timeout=5)
        self.assertEqual(created_valid.status_code, 201)
        created_id = created_valid.json()["id"]
        incompatible_patch = self.session.patch(
            f"{self.BASE_URL}/api/research-slices/{created_id}",
            json={"feature_refs": [{"feature_id": "recB"}]},
            headers=headers,
            timeout=5,
        )
        self.assertEqual(incompatible_patch.status_code, 422)

        invalid_selected_ref = self._payload()
        invalid_selected_ref["view_state"]["selected_feature_id"] = "recZ"
        response = self.session.post(f"{self.BASE_URL}/api/research-slices", json=invalid_selected_ref, headers=headers, timeout=5)
        self.assertEqual(response.status_code, 422)

    def test_round_trip_shape_preservation(self):
        headers = self._register_login(f"slice-roundtrip-{uuid4().hex}@example.com")
        created = self.session.post(f"{self.BASE_URL}/api/research-slices", json=self._payload(), headers=headers, timeout=5)
        self.assertEqual(created.status_code, 201)
        slice_id = created.json()["id"]

        loaded = self.session.get(f"{self.BASE_URL}/api/research-slices/{slice_id}", headers=headers, timeout=5)
        self.assertEqual(loaded.status_code, 200)
        body = loaded.json()

        self.assertEqual([entry["feature_id"] for entry in body["feature_refs"]], ["recA", "recB"])
        self.assertEqual(body["time_range"], {"start": 1500, "end": 1750, "mode": "range"})
        self.assertEqual(body["view_state"]["center"], [12.4964, 41.9028])
        self.assertEqual([entry["type"] for entry in body["annotations"]], ["fact", "interpretation", "hypothesis"])
        self.assertEqual(body["visibility"], "private")

    def test_read_only_share_rotation_revocation_and_public_privacy(self):
        owner_headers = self._register_login(f"slice-share-owner-{uuid4().hex}@example.com")
        outsider_headers = self._register_login(f"slice-share-outsider-{uuid4().hex}@example.com")

        created = self.session.post(
            f"{self.BASE_URL}/api/research-slices",
            json=self._payload(),
            headers=owner_headers,
            timeout=5,
        )
        self.assertEqual(created.status_code, 201, created.text)
        slice_id = created.json()["id"]

        outsider_share = self.session.post(
            f"{self.BASE_URL}/api/research-slices/{slice_id}/share",
            headers=outsider_headers,
            timeout=5,
        )
        self.assertEqual(outsider_share.status_code, 404)

        first_share = self.session.post(
            f"{self.BASE_URL}/api/research-slices/{slice_id}/share",
            headers=owner_headers,
            timeout=5,
        )
        self.assertEqual(first_share.status_code, 200, first_share.text)
        first_token = first_share.json()["share_token"]
        self.assertGreaterEqual(len(first_token), 40)
        self.assertEqual(first_share.json()["share_fragment"], f"#share={first_token}")

        db = SessionLocal()
        try:
            stored = db.query(ResearchSlice).filter(ResearchSlice.id == slice_id).one()
            self.assertNotEqual(stored.share_token_hash, first_token)
            self.assertEqual(len(stored.share_token_hash), 64)
        finally:
            db.close()

        public_session = requests.Session()
        try:
            public_get = public_session.get(
                f"{self.BASE_URL}/api/public/research-slices/shared",
                headers={"X-ARTEMIS-Share-Token": first_token},
                timeout=5,
            )
            self.assertEqual(public_get.status_code, 200, public_get.text)
            public_body = public_get.json()
            self.assertEqual(public_body["id"], slice_id)
            self.assertEqual(public_body["visibility"], "shared_read_only")
            self.assertEqual([entry["feature_id"] for entry in public_body["feature_refs"]], ["recA", "recB"])
            self.assertNotIn("owner_id", public_body)
            self.assertIn("no-store", public_get.headers.get("Cache-Control", ""))
            self.assertEqual(public_get.headers.get("Referrer-Policy"), "no-referrer")
            self.assertIn("noindex", public_get.headers.get("X-Robots-Tag", ""))

            owner_list = self.session.get(
                f"{self.BASE_URL}/api/research-slices",
                headers=owner_headers,
                timeout=5,
            )
            self.assertEqual(owner_list.status_code, 200, owner_list.text)
            self.assertTrue(owner_list.json()[0]["is_shared"])

            second_share = self.session.post(
                f"{self.BASE_URL}/api/research-slices/{slice_id}/share",
                headers=owner_headers,
                timeout=5,
            )
            self.assertEqual(second_share.status_code, 200, second_share.text)
            second_token = second_share.json()["share_token"]
            self.assertNotEqual(second_token, first_token)

            old_link = public_session.get(
                f"{self.BASE_URL}/api/public/research-slices/shared",
                headers={"X-ARTEMIS-Share-Token": first_token},
                timeout=5,
            )
            self.assertEqual(old_link.status_code, 404)
            self.assertIn("no-store", old_link.headers.get("Cache-Control", ""))

            new_link = public_session.get(
                f"{self.BASE_URL}/api/public/research-slices/shared",
                headers={"X-ARTEMIS-Share-Token": second_token},
                timeout=5,
            )
            self.assertEqual(new_link.status_code, 200, new_link.text)

            outsider_revoke = self.session.delete(
                f"{self.BASE_URL}/api/research-slices/{slice_id}/share",
                headers=outsider_headers,
                timeout=5,
            )
            self.assertEqual(outsider_revoke.status_code, 404)

            revoked = self.session.delete(
                f"{self.BASE_URL}/api/research-slices/{slice_id}/share",
                headers=owner_headers,
                timeout=5,
            )
            self.assertEqual(revoked.status_code, 204, revoked.text)

            revoked_link = public_session.get(
                f"{self.BASE_URL}/api/public/research-slices/shared",
                headers={"X-ARTEMIS-Share-Token": second_token},
                timeout=5,
            )
            self.assertEqual(revoked_link.status_code, 404)
            self.assertIn("no-store", revoked_link.headers.get("Cache-Control", ""))

            owner_list_after_revoke = self.session.get(
                f"{self.BASE_URL}/api/research-slices",
                headers=owner_headers,
                timeout=5,
            )
            self.assertFalse(owner_list_after_revoke.json()[0]["is_shared"])
        finally:
            public_session.close()


    @classmethod
    def _payload_v2(cls) -> dict:
        payload = cls._payload()
        payload.update(
            {
                "research_question": "How do the selected buildings express patronage?",
                "selection_rationale": "The pair shares a period but differs in institutional setting.",
                "evidence_state": "supported",
                "evidence_refs": [
                    {
                        "kind": "source",
                        "ref_id": "source-1",
                        "supports_finding_ids": ["ann-1"],
                    },
                    {
                        "kind": "relation",
                        "ref_id": "relation-1",
                        "supports_finding_ids": ["ann-2"],
                    },
                ],
                "findings": payload["annotations"],
                "conclusion_status": "concluded",
                "conclusion": "The comparison supports a qualified difference in patronage.",
                "uncertainty_notes": "The relation evidence is reviewed; attribution remains interpretive.",
                "saved_view": {
                    "time_range": payload["time_range"],
                    "view_state": payload["view_state"],
                    "filter_state": {"search": "patronage", "confidence": "reviewed"},
                    "comparison_feature_ids": ["recA", "recB"],
                },
                "schema_version": "2.0",
                "content_version": 1,
            }
        )
        return payload

    def test_v2_semantic_round_trip_update_and_share(self):
        headers = self._register_login(f"slice-v2-{uuid4().hex}@example.com")
        created = self.session.post(
            f"{self.BASE_URL}/api/research-slices",
            json=self._payload_v2(),
            headers=headers,
            timeout=5,
        )
        self.assertEqual(created.status_code, 201, created.text)
        body = created.json()
        self.assertEqual(body["schema_version"], "2.0")
        self.assertEqual(body["content_version"], 1)
        self.assertEqual(body["content_status"], "complete")
        self.assertEqual(body["evidence_state"], "supported")
        self.assertEqual(body["saved_view"]["filter_state"]["search"], "patronage")
        self.assertEqual(body["findings"], body["annotations"])

        slice_id = body["id"]
        patched = self.session.patch(
            f"{self.BASE_URL}/api/research-slices/{slice_id}",
            json={
                "conclusion_status": "unresolved",
                "conclusion": "",
                "uncertainty_notes": "A second source is still required.",
            },
            headers=headers,
            timeout=5,
        )
        self.assertEqual(patched.status_code, 200, patched.text)
        patched_body = patched.json()
        self.assertEqual(patched_body["content_version"], 2)
        self.assertEqual(patched_body["conclusion_status"], "unresolved")
        self.assertEqual(patched_body["research_question"], body["research_question"])
        self.assertEqual(patched_body["saved_view"], body["saved_view"])

        share = self.session.post(
            f"{self.BASE_URL}/api/research-slices/{slice_id}/share",
            headers=headers,
            timeout=5,
        )
        self.assertEqual(share.status_code, 200, share.text)
        public_get = requests.get(
            f"{self.BASE_URL}/api/public/research-slices/shared",
            headers={"X-ARTEMIS-Share-Token": share.json()["share_token"]},
            timeout=5,
        )
        self.assertEqual(public_get.status_code, 200, public_get.text)
        public_body = public_get.json()
        self.assertEqual(public_body["research_question"], body["research_question"])
        self.assertEqual(public_body["content_version"], 2)
        self.assertEqual(public_body["saved_view"]["comparison_feature_ids"], ["recA", "recB"])
        self.assertNotIn("owner_id", public_body)

    def test_v2_rejects_malformed_evidence_and_invalid_conclusion(self):
        headers = self._register_login(f"slice-v2-invalid-{uuid4().hex}@example.com")

        malformed_kind = self._payload_v2()
        malformed_kind["evidence_refs"][0]["kind"] = "similarity"
        response = self.session.post(
            f"{self.BASE_URL}/api/research-slices",
            json=malformed_kind,
            headers=headers,
            timeout=5,
        )
        self.assertEqual(response.status_code, 422)

        unsupported = self._payload_v2()
        unsupported["evidence_refs"][0]["supports_finding_ids"] = ["missing-finding"]
        response = self.session.post(
            f"{self.BASE_URL}/api/research-slices",
            json=unsupported,
            headers=headers,
            timeout=5,
        )
        self.assertEqual(response.status_code, 422)

        missing_refs = self._payload_v2()
        missing_refs["evidence_refs"] = []
        response = self.session.post(
            f"{self.BASE_URL}/api/research-slices",
            json=missing_refs,
            headers=headers,
            timeout=5,
        )
        self.assertEqual(response.status_code, 422)

        missing_conclusion = self._payload_v2()
        missing_conclusion["conclusion"] = "   "
        response = self.session.post(
            f"{self.BASE_URL}/api/research-slices",
            json=missing_conclusion,
            headers=headers,
            timeout=5,
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
