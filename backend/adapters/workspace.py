"""
Workspace Infrastructure Adapters — Decouples file generation, StrictDoc sync, test execution, and agent triggers from core domain and service logic.
Includes AbstractWorkspaceAdapter interface, LocalWorkspaceAdapter, and FakeWorkspaceAdapter.
"""

import abc
from typing import Optional, Any
from service_layer.unit_of_work import AbstractUnitOfWork

class AbstractWorkspaceAdapter(abc.ABC):
    @abc.abstractmethod
    def sync_sdoc(self, uow: AbstractUnitOfWork) -> None:
        pass

    @abc.abstractmethod
    def sync_app_shell(self, uow: AbstractUnitOfWork) -> None:
        pass

    @abc.abstractmethod
    def trigger_agent_loop(self, ticket_id: Optional[str] = None, background_tasks: Optional[Any] = None) -> None:
        pass

    @abc.abstractmethod
    def run_test_suite(self, test_id: Optional[str] = None, background_tasks: Optional[Any] = None) -> None:
        pass

    @abc.abstractmethod
    def switch_database(self, db_path: str) -> None:
        pass

    @abc.abstractmethod
    def reset_database(self) -> None:
        pass


class LocalWorkspaceAdapter(AbstractWorkspaceAdapter):
    """Real filesystem & system adapter for workspace environment."""

    def __init__(self, ws_base: Optional[str] = None):
        self.ws_base = ws_base

    def sync_sdoc(self, uow: AbstractUnitOfWork) -> None:
        try:
            from integrations.strictdoc_client import export_sdoc
            export_sdoc()
        except Exception as e:
            print(f"⚠️ Notice exporting sdoc: {e}")

    def sync_app_shell(self, uow: AbstractUnitOfWork) -> None:
        try:
            from service_layer.services import sync_workspace_app_shell
            sync_workspace_app_shell(ws_base=self.ws_base, uow=uow)
        except Exception as e:
            print(f"⚠️ Notice syncing app shell: {e}")

    def trigger_agent_loop(self, ticket_id: Optional[str] = None, background_tasks: Optional[Any] = None) -> None:
        if background_tasks is not None:
            try:
                from agent_orchestrator import run_openhands_loop
                if ticket_id:
                    background_tasks.add_task(run_openhands_loop, ticket_id)
                else:
                    background_tasks.add_task(run_openhands_loop)
            except Exception as e:
                print(f"⚠️ Notice scheduling agent loop: {e}")
        else:
            try:
                from agent_orchestrator import run_openhands_loop
                if ticket_id:
                    run_openhands_loop(ticket_id)
                else:
                    run_openhands_loop()
            except Exception as e:
                print(f"⚠️ Notice triggering agent loop: {e}")

    def run_test_suite(self, test_id: Optional[str] = None, background_tasks: Optional[Any] = None) -> None:
        try:
            from service_layer.services import run_all_tests, run_single_test
            if test_id:
                run_single_test(test_id=test_id, background_tasks=background_tasks, ws_base=self.ws_base)
            else:
                run_all_tests(background_tasks=background_tasks, ws_base=self.ws_base)
        except Exception as e:
            print(f"⚠️ Notice running test suite: {e}")

    def switch_database(self, db_path: str) -> None:
        try:
            import db.store as store
            store.set_active_db(db_path)
            store.init_db()
        except Exception as e:
            print(f"⚠️ Notice switching database: {e}")

    def reset_database(self) -> None:
        try:
            import db.store as store
            store.reset_database()
        except Exception as e:
            print(f"⚠️ Notice resetting database: {e}")


class FakeWorkspaceAdapter(AbstractWorkspaceAdapter):
    """In-memory fake workspace adapter for fast, isolated unit testing."""

    def __init__(self):
        self.sdoc_synced = False
        self.app_shell_synced = False
        self.triggered_agent_tickets = []
        self.executed_tests = []
        self.switched_db_paths = []
        self.database_reset = False

    def sync_sdoc(self, uow: AbstractUnitOfWork) -> None:
        self.sdoc_synced = True

    def sync_app_shell(self, uow: AbstractUnitOfWork) -> None:
        self.app_shell_synced = True

    def trigger_agent_loop(self, ticket_id: Optional[str] = None, background_tasks: Optional[Any] = None) -> None:
        self.triggered_agent_tickets.append(ticket_id or "ALL")

    def run_test_suite(self, test_id: Optional[str] = None, background_tasks: Optional[Any] = None) -> None:
        self.executed_tests.append(test_id or "ALL")

    def switch_database(self, db_path: str) -> None:
        self.switched_db_paths.append(db_path)

    def reset_database(self) -> None:
        self.database_reset = True

