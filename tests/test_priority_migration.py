"""Migration regressions: copied code, synthetic .env, and disposable SQLite only."""
from contextlib import closing
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from sqlalchemy import URL
from sqlalchemy.exc import OperationalError
from database_config import get_database_uri

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT.parent / 'priority-test-work'


class PriorityMigration(unittest.TestCase):
    def setUp(self):
        WORK.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=WORK)
        self.base = Path(self.temp.name).resolve()
        assert self.base.is_relative_to(WORK.resolve())
        self.project = self.base / 'project'
        (self.project / 'scripts').mkdir(parents=True)
        for name in ('app.py', 'database_config.py', 'scripts/migrate_task_priority.py'):
            shutil.copy2(ROOT / name, self.project / name)
        self.cwd = self.base / 'elsewhere'
        self.cwd.mkdir()
        self.env = dict(os.environ)
        self.env.pop('DATABASE_URL', None)
        self.env.update(SECRET_KEY='test-only-secret', USERNAME_HMAC_KEY='test-only-hmac',
                        TURNSTILE_SITE_KEY='test-only', TURNSTILE_SECRET_KEY='test-only')
        self.env['PYTHONPATH'] = os.pathsep.join([str(self.project), self.env.get('PYTHONPATH', '')])

    def tearDown(self):
        self.temp.cleanup()

    def url(self, path):
        return URL.create('sqlite', database=str(path)).render_as_string(hide_password=False)

    def seed(self, path, partial=False):
        path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(path)) as db, db:
            db.execute('CREATE TABLE user (id INTEGER PRIMARY KEY, username VARCHAR(16) UNIQUE NOT NULL, password_hash VARCHAR(255) NOT NULL)')
            db.execute('CREATE TABLE task (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES user(id), title VARCHAR(200) NOT NULL, completed BOOLEAN NOT NULL, created_at DATETIME NOT NULL)')
            db.executemany('INSERT INTO user VALUES (?,?,?)', [(1, 'owner', 'retained-hash'), (2, 'other', 'other-hash')])
            db.executemany('INSERT INTO task VALUES (?,?,?,?,?)', [(1, 1, 'First task', 0, '2026-01-02 03:04:05'), (2, 2, 'Other task', 1, '2026-01-03 03:04:05')])
            if partial:
                db.execute('ALTER TABLE task ADD COLUMN priority VARCHAR(16)')
                db.execute("UPDATE task SET priority='' WHERE id=2")
                db.execute("INSERT INTO task VALUES (3,1,'Keep high',0,'2026-01-04 00:00:00','high')")

    def run_script(self, *args, url=None):
        env = dict(self.env)
        if url is not None:
            env['DATABASE_URL'] = url
        return subprocess.run([sys.executable, str(self.project / 'scripts/migrate_task_priority.py'), *args],
                              cwd=self.cwd, env=env, capture_output=True, text=True, timeout=30)

    def digest(self, path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def app_path(self, url=None):
        env = dict(self.env)
        if url is not None:
            env['DATABASE_URL'] = url
        code = "from app import application,database; import json; context=application.app_context(); context.push(); print(json.dumps(database.engine.url.database)); database.engine.dispose(); context.pop()"
        result = subprocess.run([sys.executable, '-c', code], cwd=self.cwd, env=env,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        return Path(json.loads(result.stdout)).resolve()

    def test_default_path_matches_flask_from_another_directory(self):
        target = self.project / 'instance/secure_todo.db'
        decoy = self.cwd / 'instance/secure_todo.db'
        self.seed(target); self.seed(decoy)
        decoy_hash = self.digest(decoy)
        self.assertEqual(self.app_path(), target.resolve())
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(str(target.resolve()), result.stdout)
        self.assertEqual(self.digest(decoy), decoy_hash)

    def test_dotenv_relative_url_and_exported_absolute_override(self):
        configured = self.project / 'instance/from-env.db'
        exported = self.base / 'exported.db'
        self.seed(configured); self.seed(exported)
        dotenv = self.project / '.env'
        dotenv.write_text('DATABASE_URL=sqlite:///from-env.db\n')
        dotenv_hash = self.digest(dotenv)
        self.assertEqual(self.app_path(), configured.resolve())
        configured_hash = self.digest(configured)
        self.assertEqual(self.app_path(self.url(exported)), exported.resolve())
        self.assertEqual(self.run_script(url=self.url(exported)).returncode, 0)
        self.assertEqual(self.digest(configured), configured_hash)
        self.assertEqual(self.run_script().returncode, 0)
        self.assertEqual(self.digest(dotenv), dotenv_hash)

    def test_migration_copy_is_idempotent_and_preserves_data_and_defaults(self):
        original, copy = self.base / 'original.db', self.base / 'copy.db'
        self.seed(original)
        original_hash = self.digest(original)
        with closing(sqlite3.connect(original)) as source, closing(sqlite3.connect(copy)) as target:
            source.backup(target)
        url = self.url(copy)
        before = self.digest(copy)
        check = self.run_script('--check', url=url)
        self.assertEqual(check.returncode, 1, check.stderr)
        self.assertEqual(self.digest(copy), before)
        self.assertEqual(self.run_script(url=url).returncode, 0)
        with closing(sqlite3.connect(copy)) as db, db:
            self.assertEqual(db.execute('SELECT * FROM user ORDER BY id').fetchall(), [(1,'owner','retained-hash'),(2,'other','other-hash')])
            self.assertEqual(db.execute('SELECT id,user_id,title,completed,created_at,priority FROM task ORDER BY id').fetchall(), [(1,1,'First task',0,'2026-01-02 03:04:05','medium'),(2,2,'Other task',1,'2026-01-03 03:04:05','medium')])
            db.execute("UPDATE task SET priority='high' WHERE id=1")
            db.execute("INSERT INTO task (id,user_id,title,completed,created_at) VALUES (3,1,'Raw default',0,'2026-01-04 00:00:00')")
        self.assertEqual(self.run_script(url=url).returncode, 0)
        with closing(sqlite3.connect(copy)) as db, db:
            self.assertEqual(db.execute('SELECT priority FROM task ORDER BY id').fetchall(), [('high',),('medium',),('medium',)])
            self.assertEqual(len([c for c in db.execute('PRAGMA table_info(task)') if c[1]=='priority']), 1)
        self.assertEqual(self.run_script('--check', url=url).returncode, 0)
        self.assertEqual(self.digest(original), original_hash)

    def test_partial_column_backfill_keeps_valid_priorities(self):
        path = self.base / 'partial.db'
        self.seed(path, partial=True)
        self.assertEqual(self.run_script('--check', url=self.url(path)).returncode, 1)
        for _ in range(2):
            self.assertEqual(self.run_script(url=self.url(path)).returncode, 0)
        with closing(sqlite3.connect(path)) as db, db:
            self.assertEqual(db.execute('SELECT priority FROM task ORDER BY id').fetchall(), [('medium',),('medium',),('high',)])

    def test_missing_file_or_task_table_does_not_create_or_replace_data(self):
        path = self.base / 'missing.db'
        for args in ((), ('--check',)):
            result = self.run_script(*args, url=self.url(path))
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertFalse(path.exists())
        with closing(sqlite3.connect(path)) as db, db:
            db.execute('CREATE TABLE user (id INTEGER PRIMARY KEY)')
            db.execute('INSERT INTO user VALUES (99)')
        before = self.digest(path)
        result = self.run_script(url=self.url(path))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.digest(path), before)

    def test_dashboard_failure_is_resolved_on_an_isolated_legacy_database(self):
        path = self.base / 'legacy.db'
        self.seed(path)
        spec = importlib.util.spec_from_file_location('migration_route_test', ROOT / 'app.py')
        module = importlib.util.module_from_spec(spec)
        with patch.dict(os.environ, {**self.env, 'DATABASE_URL': self.url(path)}), patch('redis.Redis.from_url', return_value=Mock()):
            spec.loader.exec_module(module)
        app = module.application
        app.config['TESTING'] = True
        app.template_folder = str(ROOT / 'templates')
        module.limiter.enabled = False
        module.redis_client.get.return_value = '1'
        client = app.test_client()
        with client.session_transaction() as session:
            session.update(user_id=1, session_id='isolated-session', csrf_token='test-csrf')
        try:
            with self.assertRaisesRegex(OperationalError, 'no such column: task.priority'):
                client.get('/dashboard')
            result = self.run_script(url=self.url(path))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(client.get('/dashboard').status_code, 200)
            response = client.post('/tasks', data={'title':'Migrated task','priority':'high','csrf_token':'test-csrf'}, headers={'Accept':'application/json'})
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json['task']['priority'], 'high')
            task_id = response.json['task']['id']
            self.assertEqual(client.post(f'/tasks/{task_id}/toggle', data={'csrf_token':'test-csrf'}, headers={'Accept':'application/json'}).json['task']['priority'], 'high')
            self.assertEqual(client.post(f'/tasks/{task_id}/delete', data={'csrf_token':'test-csrf','confirm_delete':'yes'}, headers={'Accept':'application/json'}).status_code, 200)
            with closing(sqlite3.connect(path)) as db, db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM user').fetchone()[0], 2)
                self.assertEqual(db.execute('SELECT COUNT(*) FROM task').fetchone()[0], 2)
        finally:
            with app.app_context():
                module.database.session.remove()
                module.database.engine.dispose()

    def test_postgres_scheme_normalization_is_retained(self):
        for scheme in ('postgres://','postgresql://'):
            with patch.dict(os.environ, {'DATABASE_URL': scheme + 'test:test@localhost/test'}):
                self.assertEqual(get_database_uri(), 'postgresql+psycopg://test:test@localhost/test')


if __name__ == '__main__':
    unittest.main()
