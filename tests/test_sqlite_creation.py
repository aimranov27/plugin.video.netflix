# -*- coding: utf-8 -*-
"""Exercise schema creation without the Kodi runtime."""
import importlib.util
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sqlite3
import tempfile
import threading
import types
import unittest
from unittest.mock import Mock, patch


def load_schema_module():
    """Stub only Kodi-dependent logging and filename constants."""
    importlib.import_module('resources.lib.database')
    importlib.import_module('resources.lib.utils')
    utils = types.ModuleType('resources.lib.database.db_utils')
    utils.LOCAL_DB_FILENAME = 'nf_local.sqlite3'
    utils.SHARED_DB_FILENAME = 'nf_shared.sqlite3'
    logging = types.ModuleType('resources.lib.utils.logging')
    logging.LOG = Mock()
    spec = importlib.util.spec_from_file_location(
        'schema_under_test', Path(__file__).resolve().parents[1]
        / 'resources/lib/database/db_create_sqlite.py')
    module = importlib.util.module_from_spec(spec)
    with patch.dict('sys.modules', {
        'resources.lib.database.db_utils': utils,
        'resources.lib.utils.logging': logging,
    }):
        spec.loader.exec_module(module)
    return module


class SchemaCreationTests(unittest.TestCase):
    def test_two_first_run_callers_can_create_the_same_database(self):
        schema = load_schema_module()
        for filename, expected_count in [('nf_local.sqlite3', 7), ('nf_shared.sqlite3', 8)]:
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as directory:
                path = str(Path(directory) / filename)
                barrier = threading.Barrier(2)

                def create(db_path=path, db_name=filename, start=barrier):
                    start.wait(timeout=5)
                    schema.create_database(db_path, db_name)

                with ThreadPoolExecutor(max_workers=2) as executor:
                    tasks = [executor.submit(create) for _ in range(2)]
                    for task in tasks:
                        task.result(timeout=10)
                with sqlite3.connect(path) as connection:
                    count = connection.execute(
                        "SELECT count(*) FROM sqlite_master WHERE type='table' "
                        "AND name NOT LIKE 'sqlite_%'").fetchone()[0]
                self.assertEqual(count, expected_count)

    def test_late_creator_preserves_existing_data(self):
        schema = load_schema_module()
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / 'nf_local.sqlite3')
            schema.create_database(path, 'nf_local.sqlite3')
            with sqlite3.connect(path) as connection:
                connection.execute("INSERT INTO app_config (Name, Value) VALUES ('test', 'keep')")
            schema.create_database(path, 'nf_local.sqlite3')
            with sqlite3.connect(path) as connection:
                row = connection.execute("SELECT Value FROM app_config WHERE Name='test'").fetchone()
            self.assertEqual(row, ('keep',))


if __name__ == '__main__':
    unittest.main()
