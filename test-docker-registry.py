import requests
from typing import Tuple, Dict, Optional


class Colors:
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    ORANGE = "\033[38;5;208m"
    RED = "\033[91m"
    GREY = "\033[90m"
    ENDC = "\033[0m"  # Reset to default color


def is_docker_registry_with_headers(
    url: str, username: Optional[str] = None, password: Optional[str] = None
) -> Tuple[bool, str, Dict[str, str]]:
    try:
        # Initial request to check for Docker registry headers
        response = requests.get(f"{url}/v2/")
        headers: Dict[str, str] = response.headers
        status: int = response.status_code

        # Check specific Docker registry headers and validate their values
        expected_headers: Dict[str, str] = {
            "Docker-Distribution-Api-Version": "registry/2.0"
        }
        registry_detected: bool = all(
            headers.get(key) == value for key, value in expected_headers.items()
        )

        if not registry_detected:
            return (
                False,
                f"{Colors.RED}❌ The server is not a Docker registry.{Colors.ENDC}",
                headers,
            )

        if status == 401 and "www-authenticate" in headers:
            # Parse the WWW-Authenticate header for the Bearer token realm
            auth_header = headers["www-authenticate"]
            if "Bearer" in auth_header:
                parts = dict(
                    item.split("=", 1)
                    for item in auth_header.replace("Bearer ", "")
                    .replace('"', "")
                    .split(",")
                )
                realm = parts.get("realm")
                service = parts.get("service")

                print(f"{realm=} {service=} {parts=} {username=} {password=}")
                # Request the token
                token_response = requests.get(
                    realm,
                    params={"service": service},
                    auth=(username, password) if username and password else None,
                )
                print(f"{token_response.status_code=} {token_response.headers}")
                if token_response.status_code == 200:
                    token = token_response.json().get("token")

                    # Use the token to authenticate
                    response = requests.get(
                        f"{url}/v2/", headers={"Authorization": f"Bearer {token}"}
                    )
                    headers = response.headers
                    status = response.status_code

        if status == 200:
            return (
                True,
                f"{Colors.GREEN}✅ Docker registry detected.{Colors.ENDC}",
                headers,
            )
        elif status == 401:
            return (
                True,
                f"{Colors.ORANGE}🔒 Authentication required but server is a Docker registry.{Colors.ENDC}",
                headers,
            )
        else:
            return (
                False,
                f"{Colors.RED}❌ Unexpected response: {status} - {response.text}{Colors.ENDC}",
                headers,
            )

    except requests.exceptions.RequestException as e:
        return False, f"{Colors.RED}❌ Error: {e}{Colors.ENDC}", {}


# Example usage:
url = input(f"🔗 Enter the registry URL: ")
username = input(f"👤 Enter your username: ")
password = input(f"🔑 Enter your password: ")

result, message, headers = is_docker_registry_with_headers(url, username, password)

print("=========")
print(message)
print("=========")
print(f"📋 Headers:")
for key, value in headers.items():
    print(f"\t{Colors.GREY}{key}: {Colors.BLUE}{value}{Colors.ENDC}")
