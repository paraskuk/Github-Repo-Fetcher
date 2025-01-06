import os
import hvac


def test_vault_connection():
    vault_addr = os.getenv('VAULT_ADDR', 'http://127.0.0.1:8200')
    vault_token = os.getenv('VAULT_TOKEN')

    client = hvac.Client(
        url=vault_addr,
        token=vault_token,
        verify=False  # Set to True if using HTTPS with valid certs
    )

    if client.is_authenticated():
        print("Successfully authenticated to Vault!")
    else:
        print("Failed to authenticate to Vault.")


if __name__ == "__main__":
    test_vault_connection()

# Output: