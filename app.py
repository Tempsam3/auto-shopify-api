import os
import subprocess
import json
from flask import Flask, request, jsonify, Response

# Initialize the Flask application
app = Flask(__name__)


@app.route("/index.php", methods=["GET"])
def run_checkout():
    """
    API endpoint to run the Shopify checkout PHP script.
    Expects 'site', 'cc' and optional 'proxy' as query parameters.
    """
    # 1. Get query parameters from the request URL
    site = request.args.get("site")
    cc = request.args.get("cc")
    proxy = request.args.get("proxy")

    # 2. Validate required parameters
    if not site or not cc or not proxy:
        return jsonify(
            {
                "Response": "Error: 'site', 'cc' and 'proxy' query parameters are required."
            }
        ), 400

    # 3. Construct the command to execute the PHP script
    # Pass site, cc, and proxy as arguments
    command = ["php", "index.php", site, cc, proxy]

    try:
        # 4. Run the command as a subprocess
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=60,  # 60-second timeout
        )

        # 5. Try to parse the PHP script output as JSON
        try:
            json_output = json.loads(result.stdout)
            # Include stderr debug info if debug=1 is passed
            if request.args.get("debug") == "1" and result.stderr:
                json_output["_debug_stderr"] = result.stderr[-2000:]  # last 2000 chars
            return jsonify(json_output)
        except json.JSONDecodeError:
            return Response(result.stdout, status=500, mimetype="text/plain")

    except subprocess.CalledProcessError as e:
        return jsonify(
            {"Response": "PHP script execution failed.", "error": e.stderr}
        ), 500
    except subprocess.TimeoutExpired:
        return jsonify(
            {"Response": "Error: Script execution timed out after 60 seconds."}
        ), 504  # Gateway Timeout
    except Exception as e:
        return jsonify(
            {"Response": "An unexpected server error occurred.", "error": str(e)}
        ), 500


# This allows running the server locally for testing
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
