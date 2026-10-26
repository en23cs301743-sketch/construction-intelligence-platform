from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def test_app_runs_without_exception():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    assert len(at.tabs) == 4


def test_chatbot_demo_mode():
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.chat_input[0].set_value("How long should concrete be cured?").run()
    assert not at.exception
    assert any("cure" in m.value.lower() for m in at.chat_message[1].markdown)
