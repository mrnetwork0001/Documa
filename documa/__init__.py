"""
Documa - Autonomous Multimodal Audit & Procurement Fleet
Built for the Google All Things Agentic Hackathon.
"""

__version__ = "1.0.0"

# Load .env before anything else imports a submodule, because agents read their
# credentials from the environment at construction time. .env is gitignored, so
# a key lives on disk rather than in shell history or a pasted message.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv absent: environment variables still work
    pass
