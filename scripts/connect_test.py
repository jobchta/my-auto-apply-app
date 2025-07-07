from supabase import create_client, Client

# 1. Paste your URL and Key here
SUPABASE_URL = "https://szdmjqgigwhtxpegvhvy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN6ZG1qcWdpZ3dodHhwZWd2aHZ5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTg0NTc2MywiZXhwIjoyMDY3NDIxNzYzfQ.Hhw70MPW3457ugLWgoULisURIpaDPdA8P2i2e9D5Z6w"

try:
    # 2. This creates the connection
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Connection successful!")

    # 3. This tries to read data to prove the connection works
    response = supabase.table('users').select('id', count='exact').execute()
    print(f"✅ Found {response.count} user(s) in your database.")

except Exception as e:
    print(f"❌ Connection failed: {e}")