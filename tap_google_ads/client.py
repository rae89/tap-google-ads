import os
import json
import functools

from requests import Session
from google.auth.transport.requests import Request
from google.oauth2 import service_account

from google.ads.googleads import oauth2
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.oauth2 import _initialize_credentials_decorator, get_credentials

@_initialize_credentials_decorator
def get_service_account_credentials(service_account_info, impersonated_email):
    """
    Converts Service Account credentials as a string.
    Returns:
        A dict containing kwargs that will be provided to the
        GoogleAdsClient initializer.
    Raises:
        ValueError: If the configuration lacks a required field.
    """
    if service_account_info:
        return service_account.Credentials.from_service_account_info(json.loads(service_account_info), subject=impersonated_email, scopes=['https://www.googleapis.com/auth/adwords'])
    else:
        raise ValueError("GOOGLE_ADS_SERVICE_ACCOUNT_INFO_STRING environment variable not set")

class GoogleAdsClientServiceAccountInfo(GoogleAdsClient):
    @classmethod
    def _get_client_kwargs(cls, config_data):
        """Converts configuration dict into kwargs required by the client.
        Args:
            config_data: a dict containing client configuration.
        Returns:
            A dict containing kwargs that will be provided to the
            GoogleAdsClientServiceAccountInfo initializer.
        Raises:
            ValueError: If the configuration lacks a required field.
        """
        if config_data.get("json_key_string"):
            credentials = get_service_account_credentials(config_data.get("json_key_string"), config_data.get("impersonated_email"))
        else:
            credentials = oauth2.get_credentials(config_data)
        
        return {
            "credentials": credentials,
            "developer_token": config_data.get("developer_token"),
            "endpoint": config_data.get("endpoint"),
            "login_customer_id": config_data.get("login_customer_id"),
            "logging_config": config_data.get("logging"),
            "linked_customer_id": config_data.get("linked_customer_id"),
            "http_proxy": config_data.get("http_proxy"),
            "use_proto_plus": config_data.get("use_proto_plus"),
            "use_cloud_org_for_api_access": config_data.get(
                "use_cloud_org_for_api_access"
            ),
        }

def create_sdk_client(config, login_customer_id=None, service_auth_method=False):
    """
    Determines configuration dictionary based on authentication method.
    Args:
        config_data: a dict containing client configuration.
    Returns:
        GoogleAdsClientServiceAccount.
    """
    service_account_info = os.getenv("GOOGLE_ADS_SERVICE_ACCOUNT_INFO_STRING")
    impersonated_email = os.getenv("GOOGLE_ADS_IMPERSONATED_EMAIL")

    if service_account_info is not None:
        CONFIG = {
            "use_proto_plus": config["use_proto_plus"],
            "developer_token": config["developer_token"],
            "impersonated_email": impersonated_email,
            "json_key_string": service_account_info,
        }
    else:
        CONFIG = {
            "use_proto_plus": config["use_proto_plus"],
            "developer_token": config["developer_token"],
            "client_id": config["oauth_client_id"],
            "client_secret": config["oauth_client_secret"],
            "refresh_token": config["refresh_token"],
        }

    if login_customer_id:
        CONFIG["login_customer_id"] = login_customer_id

    sdk_client = GoogleAdsClientServiceAccountInfo.load_from_dict(CONFIG)
    return sdk_client
