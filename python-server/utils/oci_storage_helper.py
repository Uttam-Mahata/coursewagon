import os
import logging
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

OCI_NAMESPACE   = os.environ.get('OCI_NAMESPACE', 'bmevu63iwfzx')
OCI_BUCKET_NAME = os.environ.get('OCI_BUCKET_NAME', 'coursewagon-images')
OCI_REGION      = os.environ.get('OCI_REGION', 'ap-mumbai-1')
OCI_CONFIG_FILE = os.environ.get('OCI_CONFIG_FILE', os.path.expanduser('~/.oci/config'))
OCI_CONFIG_PROFILE = os.environ.get('OCI_CONFIG_PROFILE', 'DEFAULT')

# Public URL base for objects in an ObjectRead bucket
# Format: https://objectstorage.<region>.oraclecloud.com/n/<namespace>/b/<bucket>/o/<object>
PUBLIC_URL_BASE = f"https://objectstorage.{OCI_REGION}.oraclecloud.com/n/{OCI_NAMESPACE}/b/{OCI_BUCKET_NAME}/o"


class OCIStorageHelper:
    def __init__(self):
        import oci
        config = oci.config.from_file(OCI_CONFIG_FILE, OCI_CONFIG_PROFILE)
        oci.config.validate_config(config)
        self.client = oci.object_storage.ObjectStorageClient(config)
        self.namespace = OCI_NAMESPACE
        self.bucket = OCI_BUCKET_NAME
        # Verify bucket is reachable
        self.client.get_bucket(self.namespace, self.bucket)
        logger.info(f"OCI Object Storage initialized — bucket: {self.bucket} ({OCI_REGION})")

    def upload_image(self, image_bytes: bytes, path: str) -> str:
        """Upload image bytes to OCI Object Storage and return the public URL."""
        import oci
        object_name = f"{path.strip('/')}.png"
        self.client.put_object(
            namespace_name=self.namespace,
            bucket_name=self.bucket,
            object_name=object_name,
            put_object_body=BytesIO(image_bytes),
            content_type='image/png',
        )
        url = f"{PUBLIC_URL_BASE}/{object_name}"
        logger.info(f"Uploaded to OCI: {url}")
        return url

    def upload_file(self, file_bytes: bytes, path: str, content_type: str = 'application/octet-stream') -> str:
        """Upload arbitrary file bytes to OCI Object Storage and return the public URL."""
        import oci
        object_name = path.strip('/')
        self.client.put_object(
            namespace_name=self.namespace,
            bucket_name=self.bucket,
            object_name=object_name,
            put_object_body=BytesIO(file_bytes),
            content_type=content_type,
        )
        url = f"{PUBLIC_URL_BASE}/{object_name}"
        logger.info(f"Uploaded file to OCI: {url}")
        return url

    def delete_image(self, image_url: str) -> bool:
        """Delete an object given its public URL."""
        try:
            # Extract object name from URL
            prefix = f"{PUBLIC_URL_BASE}/"
            if not image_url.startswith(prefix):
                logger.warning(f"URL does not match OCI bucket: {image_url}")
                return False
            object_name = image_url[len(prefix):]
            self.client.delete_object(
                namespace_name=self.namespace,
                bucket_name=self.bucket,
                object_name=object_name,
            )
            logger.info(f"Deleted OCI object: {object_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting OCI object: {str(e)}")
            return False
