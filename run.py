import os
from app.app import app
app.run(port=int(os.getenv("PORT", 5050)), debug=True)
