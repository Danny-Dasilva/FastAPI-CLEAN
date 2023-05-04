from pydantic import BaseSettings, root_validator
import json
import base64
from google.oauth2 import service_account
from typing import Optional
class Config(BaseSettings):
    """Config for general env attributes
    """

    DATASTORE_AUTH_BASE64: str = ""

    @root_validator()
    def root_validation(cls, values):
        if values.get("DATASTORE_AUTH_BASE64"):
            values["CREDENTIALS"] = json.loads(base64.b64decode(values["DATASTORE_AUTH_BASE64"]))
        return values

    @property
    def NAMESPACE(self) -> Optional[str]:
        return 
    @property
    def PROJECT_ID(self) -> str:
        return self.CREDENTIALS.get("project_id")

    @property
    def TYPE(self) -> str:
        return self.CREDENTIALS.get("type")

    @property
    def PRIVATE_KEY_ID(self) -> str:
        return self.CREDENTIALS.get("private_key_id")

    @property
    def PRIVATE_KEY(self) -> str:
        return self.CREDENTIALS.get("private_key")

    @property
    def CLIENT_EMAIL(self) -> str:
        return self.CREDENTIALS.get("client_email")

    @property
    def CLIENT_ID(self) -> str:
        return self.CREDENTIALS.get("client_id")

    @property
    def AUTH_URI(self) -> str:
        return self.CREDENTIALS.get("auth_uri")

    @property
    def TOKEN_URI(self) -> str:
        return self.CREDENTIALS.get("token_uri")

    @property
    def AUTH_PROVIDER_X509_CERT_URL(self) -> str:
        return self.CREDENTIALS.get("auth_provider_x509_cert_url")

    @property
    def CLIENT_X509_CERT_URL(self) -> str:
        return self.CREDENTIALS.get("client_x509_cert_url")


    @property
    def service_credentials(self) -> str:
        """Get Google service credentials"""
        return service_account.Credentials.from_service_account_info(self.CREDENTIALS)

    class Config:
        env_file = '.env'
config = Config()