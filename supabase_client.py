from supabase import create_client, Client

url = "https://pufgxmvvddqzxpjrqxpm.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # tu anon key completa

supabase: Client = create_client(url, key)
