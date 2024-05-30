import os
import json
from google.ads.googleads.client import GoogleAdsClient
from google.oauth2 import service_account
import ast

def get_service_account_credentials():
    """
    Converts Service Account credentials as a string.

    Returns:
        A dict containing kwargs that will be provided to the
        GoogleAdsClient initializer.

    Raises:
        ValueError: If the configuration lacks a required field.
    """
    service_account_info_str = os.getenv("PRIVATE_KEY")
    service_account_info = json.loads(service_account_info_str)
    if service_account_info:
        return service_account.Credentials.from_service_account_info(service_account_info)
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
            "credentials": get_service_account_credentials(),
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

    if config.get("auth_method") == "Service_Account":
        CONFIG = {
            "use_proto_plus": False,
            "developer_token": config["developer_token"],
            "json_key_file_path": get_service_account_credentials(),
            "impersonated_email": config["impersonated_email"],
        }

    else:
        CONFIG = {
            "use_proto_plus": False,
            "developer_token": config["developer_token"],
            "client_id": config["oauth_client_id"],
            "client_secret": config["oauth_client_secret"],
            "refresh_token": config["refresh_token"],
        }

    # if login_customer_id:
        # CONFIG["login_customer_id"] = login_customer_id

    sdk_client = GoogleAdsClientServiceAccount.load_from_dict(CONFIG)
    return sdk_client
