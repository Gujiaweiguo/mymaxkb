import requests

from django.utils.translation import gettext_lazy as _

from common.exception.app_exception import AppApiException


class LarkClient:
    base_url = "https://open.feishu.cn/open-apis"

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret

    def _post(
        self, path: str, json_data: dict | None = None, headers: dict | None = None
    ):
        response = requests.post(
            f"{self.base_url}{path}",
            json=json_data or {},
            headers=headers or {},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("code") not in (0, "0", None):
            raise AppApiException(500, payload.get("msg") or _("Lark request failed"))
        return payload.get("data", {})

    def _get(self, path: str, params: dict | None = None, headers: dict | None = None):
        response = requests.get(
            f"{self.base_url}{path}",
            params=params or {},
            headers=headers or {},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("code") not in (0, "0", None):
            raise AppApiException(500, payload.get("msg") or _("Lark request failed"))
        return payload.get("data", {})

    def get_tenant_access_token(self):
        data = self._post(
            "/auth/v3/tenant_access_token/internal",
            json_data={"app_id": self.app_id, "app_secret": self.app_secret},
        )
        token = data.get("tenant_access_token")
        if not token:
            raise AppApiException(500, _("Failed to get Lark tenant access token"))
        return token

    def _auth_headers(self):
        return {"Authorization": f"Bearer {self.get_tenant_access_token()}"}

    def list_folder_files(self, folder_token: str):
        files = []
        page_token = None
        visited_page_tokens = set()

        while True:
            params = {"folder_token": folder_token, "page_size": 200}
            if page_token:
                if page_token in visited_page_tokens:
                    raise AppApiException(
                        500, _("Invalid Lark folder pagination state")
                    )
                visited_page_tokens.add(page_token)
                params["page_token"] = page_token

            data = self._get(
                "/drive/v1/files",
                params=params,
                headers=self._auth_headers(),
            )
            files.extend(data.get("files", []))

            has_more = data.get("has_more")
            next_page_token = data.get("next_page_token") or data.get("page_token")
            if not has_more:
                break
            if not next_page_token:
                raise AppApiException(500, _("Missing Lark folder pagination token"))
            page_token = next_page_token

        return files

    def get_docx_raw_content(self, document_token: str):
        data = self._get(
            f"/docx/v1/documents/{document_token}/raw_content",
            headers=self._auth_headers(),
        )
        return data.get("content", "")

    def get_document_content(self, token: str, file_type: str):
        if file_type == "docx":
            return self.get_docx_raw_content(token)
        raise AppApiException(
            500, _("Only Lark docx documents are supported for import")
        )
