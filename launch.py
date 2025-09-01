import sys
import subprocess
import time



command = [
    sys.executable,  # Use the same python that is running this script
    "-m",            # Run the uvicorn module
    "uvicorn",
    "src.interface.app:app",
    "--reload"
]

print(f"🚀 Starting server with command: {' '.join(command)}")

try:
    # --- Using subprocess.Popen ---
    # Popen starts the process and immediately returns. It doesn't wait for the command to complete.
    # This is ideal for starting a long-running server.
    server_process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE, # Capture standard output
        stderr=subprocess.PIPE, # Capture standard error
        text=True               # Decode output as text
    )

    print(f"✅ Server process started with PID: {server_process.pid}")
    print("Watching server output... (Press Ctrl+C to stop)")

    # You can monitor the server's output in real-time if you wish
    # This part is optional but useful for debugging
    while True:
        # You can add logic here to check the server's health or do other tasks
        time.sleep(5)


except KeyboardInterrupt:
    print("\n🛑 Stopping server...")
    server_process.terminate() # Send a termination signal
    server_process.wait()      # Wait for the process to fully close
    print("✅ Server stopped.")

except FileNotFoundError:
    print("\\nERROR: 'uvicorn' or python executable not found.")
    print("Please ensure you have activated your virtual environment (.venv\\Scripts\\activate).")
    sys.exit(1)

except Exception as e:
    print(f"An unexpected error occurred: {e}")
    if 'server_process' in locals():
        server_process.terminate()
    sys.exit(1)