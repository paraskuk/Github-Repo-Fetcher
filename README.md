# GitHub User Profile and Repository Language Aggregator

This project fetches a GitHub user's profile information and aggregates the programming languages used across all their public repositories. It uses HashiCorp Vault to securely store and retrieve the GitHub personal access token.

## Features

- Fetch GitHub user profile information
- Retrieve all public repositories of a user
- Aggregate programming languages used across repositories
- Securely store and retrieve GitHub token using HashiCorp Vault

## Prerequisites

- Python 3.x
- HashiCorp Vault
- GitHub personal access token

## Installation


2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Ensure `hvac` is installed:
    ```sh
    pip install hvac
    ```

## Configuration

1. Set up HashiCorp Vault and store your GitHub token:
    ```sh
    export VAULT_ADDR='http://127.0.0.1:8200'
    export VAULT_TOKEN='your-vault-token'
    vault kv put secret/github token='your-github-token'
    ```

2. Set the environment variables:
    ```sh
    export VAULT_ADDR='http://127.0.0.1:8200'
    export VAULT_TOKEN='your-vault-token'
    ```

## Usage

Run the main script with the GitHub username as an argument:
```sh
python main.py <github-username>
```

Example:
```sh
python main.py octocat
```

## Testing

To test the Vault connection, run the `test_vault_conn.py` script:
```sh
python test_vault_conn.py
```

## Project Structure

- `main.py`: Main script to fetch and display GitHub user profile and repository languages.
- `test_vault_conn.py`: Script to test the connection to HashiCorp Vault.
- `requirements.txt`: List of required Python packages.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.