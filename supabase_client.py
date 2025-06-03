from supabase import create_client, Client

url = "https://pufgxmvvddqzxpjrqxpm.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB1Zmd4bXZ2ZGRxenhwanJxeHBtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc3NjkzODgsImV4cCI6MjA2MzM0NTM4OH0.dnbj810dalr1VZ0je_LsBKddbb3LetY828sc8mSbaNU"  # tu anon key completa

supabase: Client = create_client(url, key)
