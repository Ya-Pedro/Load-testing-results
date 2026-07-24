from locust import HttpUser, task, between, LoadTestShape
import random


class StepLoadShape(LoadTestShape):
    stages = [
        {"duration": 225, "users": 100,  "spawn_rate": 10},
        {"duration": 450, "users": 250,  "spawn_rate": 15},
        {"duration": 675, "users": 500,  "spawn_rate": 20},
        {"duration": 900, "users": 1000, "spawn_rate": 25},
    ]

    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                return stage["users"], stage["spawn_rate"]
        return None


class SmartSearchUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        self.api_key = "on_GYKrEvf5OupqP45RM4RjWWmxInsBcCWBvDDsJcezkLNjJwsyfolertbdMnQdjlKp-JRRfGC2Mvt72nrDj_FSmj3eWzUOdiYYVfDh6jrmfbAvmL0JaUpX1brTj6sz1oPqod1hnPL5ongV3QWBJ4IJMwQw-bZXcBP_h_Do8-w5167LXsPV5qPVeWMUBvlE9mfQmsplS9aGErfKBa9XvfhMJTqNxYeseyDzYwqMCh6wFgv0WaMCLrhlyKCLog0Gnct7"
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": self.api_key
        }

        self.user_ids = [
            "850c6251-6461-4694-a073-f9850ce27d59"
        ]

        self.session_ids = [
            "1e7b33c4-e59b-4297-b76f-2f4e08d5267d",
            "17e678f5-3141-4203-839f-8aee144c8ec8",
            "fc2c2db0-dc33-42a0-bcf0-a5e0d03ec33a"
        ]

        self.created_session_ids = []

        resp = self.client.post(
            "/api/chat/create-chat-session",
            json={"persona_id": 0, "description": "locust init"},
            headers=self.headers,
            name="/api/chat/create-chat-session"
        )
        if resp.status_code == 200:
            try:
                sid = resp.json().get("chat_session_id")
                if sid:
                    self.created_session_ids.append(sid)
            except Exception:
                pass

        self.send_message_payload = {
            "chunks_above": 0,
            "chunks_below": 0,
            "full_doc": False,
            "parent_message_id": None,
            "message": "Что такое SmartSearch?",
            "file_descriptors": [],
            "user_file_ids": [],
            "user_folder_ids": [],
            "prompt_id": None,
            "search_doc_ids": None,
            "retrieval_options": {
                "run_search": "always",
                "real_time": True,
                "filters": {},
                "enable_auto_detect_filters": True,
                "offset": 0,
                "limit": 10,
                "dedupe_docs": False
            },
            "use_existing_user_message": False,
            "force_user_file_search": False,
            "use_agentic_search": False,
            "skip_gen_ai_answer_generation": False
        }

        self.test_messages = [
            "Что такое SmartSearch?",
            "Как работает поиск по документам?",
            "Расскажи о возможностях системы",
            "Найди информацию о политике безопасности",
            "Как настроить коннекторы?",
        ]


    @task(5)
    def get_chat_sessions(self):
        user_id = random.choice(self.user_ids)
        self.client.get(
            f"/api/admin/chat-sessions?user_id={user_id}",
            headers=self.headers,
            name="/api/admin/chat-sessions"
        )

    @task(4)
    def get_chat_session_history(self):
        session_id = random.choice(self.session_ids)
        self.client.get(
            f"/api/admin/chat-session-history/{session_id}",
            headers=self.headers,
            name="/api/admin/chat-session-history/{chat_session_id}"
        )

    @task(3)
    def get_llm_provider(self):
        self.client.get(
            "/api/admin/llm/provider",
            headers=self.headers,
            name="/api/admin/llm/provider"
        )

    @task(3)
    def get_connector_indexing_status(self):
        self.client.get(
            "/api/manage/admin/connector/indexing-status",
            headers=self.headers,
            name="/api/manage/admin/connector/indexing-status"
        )

    @task(2)
    def get_tools(self):
        self.client.get(
            "/api/tool",
            headers=self.headers,
            name="/api/tool"
        )

    @task(2)
    def get_settings(self):
        self.client.get(
            "/api/settings",
            headers=self.headers,
            name="/api/settings"
        )


    @task(2)
    def send_message_llm_flow(self):
        if not self.created_session_ids:
            return
        payload = self.send_message_payload.copy()
        payload["chat_session_id"] = random.choice(self.created_session_ids)
        payload["message"] = random.choice(self.test_messages)
        self.client.post(
            "/api/chat/send-message",
            json=payload,
            headers=self.headers,
            name="/api/chat/send-message [LLM flow]"
        )


    @task(1)
    def telegram_send_message(self):
        if not self.created_session_ids:
            return
        payload = self.send_message_payload.copy()
        payload["chat_session_id"] = random.choice(self.created_session_ids)
        payload["message"] = random.choice(self.test_messages)
        self.client.post(
            f"/api/telegram/send-message?token={self.api_key}",
            json=payload,
            headers=self.headers,
            name="/api/telegram/send-message"
        )


    @task(2)
    def create_chat_session(self):
        with self.client.post(
            "/api/chat/create-chat-session",
            json={"persona_id": 0, "description": "string"},
            headers=self.headers,
            name="/api/chat/create-chat-session",
            catch_response=True
        ) as resp:
            if resp.status_code == 200:
                try:
                    sid = resp.json().get("chat_session_id")
                    if sid:
                        self.created_session_ids.append(sid)
                        if len(self.created_session_ids) > 50:
                            self.created_session_ids.pop(0)
                except Exception:
                    pass
                resp.success()

    @task(2)
    def rename_chat_session(self):
        if not self.created_session_ids:
            return
        payload = {
            "chat_session_id": random.choice(self.created_session_ids),
            "name": "locust test"
        }
        self.client.put(
            "/api/chat/rename-chat-session",
            json=payload,
            headers=self.headers,
            name="/api/chat/rename-chat-session"
        )

    @task(3)
    def query_user_searches(self):
        self.client.get(
            "/api/query/user-searches",
            headers=self.headers,
            name="/api/query/user-searches"
        )

    @task(2)
    def query_document_search(self):
        payload = {
            "message": random.choice(self.test_messages),
            "search_type": "semantic",
            "retrieval_options": {
                "run_search": "always",
                "real_time": True,
                "filters": {},
                "enable_auto_detect_filters": True,
                "offset": 0,
                "limit": 10,
                "dedupe_docs": False
            },
            "evaluation_type": "basic"
        }
        self.client.post(
            "/api/query/document-search",
            json=payload,
            headers=self.headers,
            name="/api/query/document-search"
        )

    @task(3)
    def get_manage_admin_connector(self):
        self.client.get(
            "/api/manage/admin/connector",
            headers=self.headers,
            name="/api/manage/admin/connector"
        )

    @task(1)
    def run_connector_once(self):
        self.client.post(
            "/api/manage/admin/connector/run-once",
            json={"connector_id": 1},
            headers=self.headers,
            name="/api/manage/admin/connector/run-once"
        )
