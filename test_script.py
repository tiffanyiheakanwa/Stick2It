import sys
sys.path.append('.')
import asyncio
from backend.app.database import get_db_session
from backend.app.main import get_nudges

async def test():
    result = await get_nudges(1, "dashboard", 1)
    print(result)

asyncio.run(test())
