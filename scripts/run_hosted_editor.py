"""Run the reviewed hosted editor with exactly one worker (TLS at provider edge)."""
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

if __name__ == "__main__":
    from app.knowledge_editor.hosted import create_app
    import uvicorn
    port = int(os.getenv("PORT", "10000"))
    if not 1 <= port <= 65535:
        raise RuntimeError("Invalid listening port")
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=port, workers=1,
                proxy_headers=False, access_log=False, log_config=None)
