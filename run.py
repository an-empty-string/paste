import os
from app.app import app
app.run(port=os.getenv("PORT", 5050), debug=True)
