import sys
from app import create_app

# Ensure the parent directory is in the Python path
sys.path.append('.')

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
