from supabase import create_client, Client

from config import get_supabase_url, get_supabase_key


class SuperBaseService:
    # Initialize Supabase client with credentials from environment variables
    url: str = get_supabase_url()
    key: str = get_supabase_key()
    sp: Client = create_client(url, key)
            
    @staticmethod
    def download_file(bucket: str, file_path: str) -> str:
        return SuperBaseService.sp.storage.from_(bucket).download(file_path)
    
    @staticmethod
    def upload_file(bucket: str, file_path: str, local_path: str, content_type: str = None) -> dict:
        with open(local_path, "rb") as f:
            data = f.read()
        
        return SuperBaseService.upload_bytes(
            bucket=bucket,
            file_path=file_path,
            data=data,
            content_type=content_type,
        )
    
    @staticmethod
    def upload_bytes(bucket: str, file_path: str, data: bytes, content_type: str = None, upsert: bool = False) -> dict:
        file_options = {}
        if content_type:
            file_options["content-type"] = content_type
        if upsert is not None:
            file_options["upsert"] = "true" if upsert else "false"
        
        return SuperBaseService.sp.storage.from_(bucket).upload(
            file_path,
            data,
            file_options=file_options
        )
    
    @staticmethod
    def get_public_url(bucket: str, file_path: str) -> str:
        return SuperBaseService.sp.storage.from_(bucket).get_public_url(file_path)