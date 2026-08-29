"""Test isolation.

documa/__init__ loads .env at import time, so on a machine with Application
Default Credentials configured the suite reaches out to Google: the vision agent
calls Vertex AI, and FirestoreService and StorageService open real clients. A 40
second suite became a 17 minute one that costs money and fails offline.

These tests exercise Documa's own logic, not Google's. Credentials are stripped
here at conftest import - which pytest performs before importing any test module
or the package under test - so the fleet runs on its deterministic fixtures and
the services use their in-memory and local-disk fallbacks. Live model behaviour
is verified separately against the deployed service.
"""

import os

for _var in (
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "GOOGLE_GENAI_USE_VERTEXAI",
    "GOOGLE_CLOUD_PROJECT",
    "GOOGLE_CLOUD_LOCATION",
    "DOCUMA_STRICT_MODE",
):
    os.environ.pop(_var, None)

# Pointing at a path that does not exist makes google.auth fail immediately with
# DefaultCredentialsError instead of discovering the gcloud ADC file, so the
# Firestore and Storage clients take their documented fallback paths at once
# rather than making live calls.
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/nonexistent/documa-tests-no-adc.json"
os.environ["DOCUMA_DISABLE_TRIAGE"] = "true"
os.environ["DOCUMA_SKIP_DOTENV"] = "true"
