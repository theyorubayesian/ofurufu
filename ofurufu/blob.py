import os

from azure.storage.blob import BlobServiceClient

CONNECTION_STRING_FORMAT = "DefaultEndpointsProtocol=https;AccountName={account_name};" \
                           "AccountKey={account_key};EndpointSuffix=core.windows.net"


def authenticate_blob_client(account_name: str, account_key: str) -> BlobServiceClient:
    return BlobServiceClient.from_connection_string(
        CONNECTION_STRING_FORMAT.format(
            account_name=account_name,
            account_key=account_key
        )
    )


def upload_blob(file_path: str, container: str, client: BlobServiceClient, dest_path: str = None):
    dest_path = dest_path or os.path.split(file_path)[1]
    blob_client = client.get_blob_client(
        container=container,
        blob=dest_path
    )
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data)

    return blob_client.url


def download_blob(client: BlobServiceClient, container: str, filename: str, download_dir: str):
    blob_client = client.get_blob_client(container, filename)

    path = os.path.join(download_dir, filename)
    with open(path, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())