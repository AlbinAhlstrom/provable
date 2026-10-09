"""Backend startup must never generate a UI from the default pitch (it blocked the port for minutes)."""

from unittest.mock import patch

from service_layer import services
from service_layer.unit_of_work import FakeUnitOfWork


def test_startup_does_not_generate_a_ui_when_nothing_was_synthesized(tmp_path):
    """Verify an unsynthesized kickstart state (fresh or just reset) triggers no UI generation at startup.

    id: TST-START-001
    Given: A default kickstart state (default pitch, nothing synthesized) and a workspace
    When: The startup shell sync runs
    Then: No LLM UI generation is attempted and App.tsx is untouched
    """
    (tmp_path / "src").mkdir()
    app = tmp_path / "src" / "App.tsx"
    app.write_text("export default function App() { return null; }", encoding="utf-8")
    with patch("onboarding.ui_generator.generate_llm_ui") as llm:
        services.sync_workspace_app_shell_on_startup(ws_base=str(tmp_path), uow=FakeUnitOfWork())
    llm.assert_not_called()
    assert app.read_text(encoding="utf-8") == "export default function App() { return null; }"


def test_startup_syncs_the_shell_for_a_synthesized_domain(tmp_path):
    """Verify a synthesized state still has its shell synchronised at startup.

    id: TST-START-002
    Given: A synthesized kickstart state
    When: The startup shell sync runs
    Then: The regular shell sync is invoked for that workspace
    """
    uow = FakeUnitOfWork()
    with uow:
        state = uow.kickstart.get()
        state.synthesized = True
        uow.kickstart.save(state)
        uow.commit()
    with patch.object(services, "sync_workspace_app_shell") as sync:
        services.sync_workspace_app_shell_on_startup(ws_base=str(tmp_path), uow=uow)
    sync.assert_called_once()
