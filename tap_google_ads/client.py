import os
import json
import functools
from google.auth.transport.requests import Request
from requests import Session
from google.ads.googleads.client import GoogleAdsClient
from google.oauth2 import service_account

def _initialize_credentials_decorator(func):
    """A decorator used to easily initialize credentials objects.

    Returns:
        An initialized credentials instance
    """

    @functools.wraps(func)
    def initialize_credentials_wrapper(*args, **kwargs):
        credentials = func(*args, **kwargs)
        # If the configs contain an http_proxy, refresh credentials through the
        # proxy URI
        proxy = kwargs.get("http_proxy")
        if proxy:
            session = Session()
            session.proxies.update({"http": proxy, "https": proxy})
            credentials.refresh(Request(session=session))
        else:
            credentials.refresh(Request())
        return credentials

    return initialize_credentials_wrapper


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
        raise ValueError("SERVICE_ACCOUNT_INFO_STRING environment variable not set")

class GoogleAdsClientServiceAccount(GoogleAdsClient):
    @classmethod
    def _get_client_kwargs(cls, config_data):
        """Converts configuration dict into kwargs required by the client.

        Args:
            config_data: a dict containing client configuration.

        Returns:
            A dict containing kwargs that will be provided to the
            GoogleAdsClientServiceAccount initializer.

        Raises:
            ValueError: If the configuration lacks a required field.
        """
        return {
            "credentials": get_service_account_credentials(config_data.get("json_key_file_path"), config_data.get("impersonated_email")),
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


def create_sdk_client(config, login_customer_id=None, auth_method=None):
    """
    Determines configuration dictionary based on authentication method.

    Args:
        config_data: a dict containing client configuration.

    Returns:
        GoogleAdsClientServiceAccount.
    """
    service_account_info = os.getenv("SERVICE_ACCOUNT_INFO_STRING")
    impersonated_email = os.getenv("GOOGLE_ADS_IMPERSONATED_EMAIL")
    
    if config.get("auth_method") == "Service_Account":
        CONFIG = {
            "use_proto_plus": config["use_proto_plus"],
            "developer_token": config["developer_token"],
            "impersonated_email": impersonated_email,
            "json_key_file_path": service_account_info,
            # "login_customer_id": config["login_customer_id"],
        }
    else:
        CONFIG = {
            "use_proto_plus": config["use_proto_plus"],
            "developer_token": config["developer_token"],
            "client_id": config["oauth_client_id"],
            "client_secret": config["oauth_client_secret"],
            "refresh_token": config["refresh_token"],
            # "login_customer_id": config["login_customer_id"],
        }

    if login_customer_id:
        CONFIG["login_customer_id"] = login_customer_id

    sdk_client = GoogleAdsClientServiceAccount.load_from_dict(CONFIG)
    return sdk_client
