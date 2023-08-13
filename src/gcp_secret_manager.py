import logging

from google.cloud import secretmanager

logger = logging.getLogger(__name__)


class GCPSecretsManager:
    def __init__(self, project_id="main-pj-al"):
        self.project_id = project_id
        self.client = secretmanager.SecretManagerServiceClient()

    def access_secret_version(self, secret_id, version_id="latest"):
        # Build the resource name of the secret version
        secret_name = self.client.secret_version_path(
            self.project_id, secret_id, version_id
        )

        # Access the secret version
        response = self.client.access_secret_version(request={"name": secret_name})

        # Get the payload (secret value)
        payload = response.payload.data.decode()
        return payload

    def add_secret_version(self, secret_id, secret_value):
        """
        Update the value of an existing secret in Google Cloud Secret Manager.

        Args:
            project_id (str): The ID of your Google Cloud project.
            secret_id (str): The ID of the secret you want to update.
            secret_value (str): The new value to set for the secret.

        Returns:
            None
        """
        # Build the secret name using the project and secret IDs.
        parent = self.client.secret_path(self.project_id, secret_id)

        # Build the secret payload with the updated value.
        payload = secret_value.encode()

        # Update the secret with the new payload.
        response = self.client.add_secret_version(
            request={
                "parent": parent,
                "payload": {
                    "data": payload,
                },
            }
        )
        version = int(response.name.split("/")[-1])
        prev_version = version - 1
        self._destroy_secret_version(secret_id, prev_version)
        logger.info("Added token version and destroyed previous version")
        return response

    def _destroy_secret_version(self, secret_id, version_id: int):
        """
        Destroy the given secret version, making the payload irrecoverable. Other
        secrets versions are unaffected.
        """
        # Build the resource name of the secret version
        name = self.client.secret_version_path(
            self.project_id, secret_id, str(version_id)
        )

        # Destroy the secret version.
        self.client.destroy_secret_version(request={"name": name})
