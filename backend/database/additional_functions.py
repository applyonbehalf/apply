# database/additional_functions.py - Additional database functions needed for the processor
# Add these functions to your database/connection.py file

async def get_application_by_id(self, app_id: str) -> Optional[dict]:
    """Get application by ID"""
    response = self.supabase.table('job_applications').select('*').eq('id', app_id).execute()
    return response.data[0] if response.data else None

async def get_captcha_session(self, session_id: str) -> Optional[dict]:
    """Get CAPTCHA session by ID"""
    response = self.supabase.table('captcha_sessions').select('*').eq('id', session_id).execute()
    return response.data[0] if response.data else None

async def get_batch_by_id(self, batch_id: str) -> Optional[dict]:
    """Get batch by ID"""
    response = self.supabase.table('application_batches').select('*').eq('id', batch_id).execute()
    return response.data[0] if response.data else None

async def get_user_applications_since(self, user_id: str, since_date: datetime) -> List[dict]:
    """Get user applications since a specific date"""
    response = (
        self.supabase.table('job_applications')
        .select('*')
        .eq('user_id', user_id)
        .gte('created_at', since_date.isoformat())
        .execute()
    )
    return response.data or []

# Add these functions to your database/connection.py DatabaseConnection class