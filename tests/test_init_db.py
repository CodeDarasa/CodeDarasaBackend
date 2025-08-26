from app.init_db import init
from app.db import base, session
    
def test_init_creates_tables(monkeypatch):
    """Test that init() calls Base.metadata.create_all with the engine."""

    called = {}

    def fake_create_all(bind=None):
        called["bind"] = bind

    monkeypatch.setattr(base.Base.metadata, "create_all", fake_create_all)
    init()
    assert called["bind"]
