import os

class s3_sync:
    def sync_folder_to_s3(self, folder,aws_bucket_url):
        """
        Sync a local folder to an S3 bucket folder.
        
        Args:
            folder (str): The path to the local folder to sync.
            aws_bucket_url (str): The URL of the S3 bucket folder where files will be synced.
        """
        command = f"aws s3 sync {folder} {aws_bucket_url}"

        os.system(command)  


    def sync_folder_from_s3(self, folder,aws_bucket_url):
        """
        Sync a local folder from an S3 bucket folder.
        
        Args:
            folder (str): The path to the local folder to sync.
            aws_bucket_url (str): The URL of the S3 bucket folder where files will be synced.
        """
        command = f"aws s3 sync {aws_bucket_url} {folder}"

        os.system(command)