import sys
import subprocess
import time
import os

from src import main

if __name__ == "__main__":
    main.generate_pipeline()
    command = [
        "uvicorn",
        "src.interface.app:app",
        "--reload"
    ]
    try:
        subprocess.run(command, check=True)
    except FileNotFoundError:
        print("\n❌ Error: 'uvicorn' command not found.")
        print("   Please ensure you have installed all dependencies from requirements.txt:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ The web server failed to start. Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n shutting down the server.")
        sys.exit(0)