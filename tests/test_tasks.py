"""Task route regressions using SQLite in memory and a mocked Redis boundary."""
import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import patch, Mock


class TaskRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = Path(__file__).resolve().parents[1] / 'app.py'
        spec = importlib.util.spec_from_file_location('fernward_task_tests', source)
        cls.module = importlib.util.module_from_spec(spec)
        with patch.dict(os.environ, {
            'SECRET_KEY': 'isolated-test-secret', 'USERNAME_HMAC_KEY': 'test-hmac',
            'TURNSTILE_SITE_KEY': 'test-only', 'TURNSTILE_SECRET_KEY': 'test-only',
            'DATABASE_URL': 'sqlite:///:memory:', 'REDIS_URL': 'redis://127.0.0.1:6379/15'
        }), patch('redis.Redis.from_url', return_value=Mock()):
            spec.loader.exec_module(cls.module)
        cls.app = cls.module.application
        cls.app.template_folder = str(source.parent / 'templates')
        cls.app.static_folder = str(source.parent / 'static')
        cls.app.config.update(TESTING=True)
        cls.module.limiter.enabled = False

    def setUp(self):
        m = self.module
        self.context = self.app.app_context()
        self.context.push()
        m.database.drop_all()
        m.database.create_all()
        m.database.session.add_all([
            m.User(id=1, username='owner', password_hash='not-a-real-password'),
            m.User(id=2, username='other', password_hash='not-a-real-password')
        ])
        m.database.session.commit()
        m.redis_client.get.side_effect = None
        m.redis_client.get.return_value = '1'
        self.client = self.app.test_client()
        with self.client.session_transaction() as session:
            session.update(user_id=1, session_id='test-session', csrf_token='test-csrf')

    def tearDown(self):
        self.module.database.session.remove()
        self.context.pop()

    def post(self, path, data=None, json=True):
        return self.client.post(path, data={'csrf_token': 'test-csrf', **(data or {})},
                                headers={'Accept': 'application/json' if json else 'text/html'})

    def task(self, owner=1):
        m = self.module
        task = m.Task(user_id=owner, title='A task')
        m.database.session.add(task)
        m.database.session.commit()
        return task

    def test_creation_json_persists_and_escapes(self):
        title = '<img src=x onerror=alert(1)> & tea'
        response = self.post('/tasks', {'title': title})
        self.assertEqual(response.status_code, 201)
        task = response.json['task']
        self.assertEqual(task['title'], title)
        self.assertFalse(task['completed'])
        self.assertEqual(self.module.database.session.get(self.module.Task, task['id']).user_id, 1)
        page = self.client.get('/dashboard').get_data(as_text=True)
        self.assertIn('&lt;img', page)
        self.assertNotIn('<img src=x', page)
        self.assertIn('data-task-delete', page)

    def test_validation_in_both_formats(self):
        for json in (True, False):
            for title in ('', '  ', 'x' * 201):
                self.assertEqual(self.post('/tasks', {'title': title}, json).status_code, 400)
        self.assertEqual(self.post('/tasks', {'title': 'x' * 200}).status_code, 201)

    def test_csrf_for_every_mutation_in_both_formats(self):
        task = self.task()
        for json in (True, False):
            for path in ('/tasks', f'/tasks/{task.id}/toggle', f'/tasks/{task.id}/delete'):
                response = self.post(path, {'title': 'Blocked', 'csrf_token': 'wrong', 'confirm_delete': 'yes'}, json)
                self.assertEqual(response.status_code, 403)
        self.assertFalse(task.completed)
        self.assertIsNotNone(self.module.database.session.get(self.module.Task, task.id))

    def test_other_users_tasks_are_inaccessible(self):
        task = self.task(owner=2)
        for json in (True, False):
            for action in ('toggle', 'delete'):
                self.assertEqual(self.post(f'/tasks/{task.id}/{action}', {'confirm_delete': 'yes'}, json).status_code, 404)
        self.assertFalse(task.completed)
        self.assertNotIn('A task', self.client.get('/dashboard').get_data(as_text=True))

    def test_completion_and_reversal(self):
        task = self.task()
        for completed in (True, False):
            response = self.post(f'/tasks/{task.id}/toggle')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['task']['completed'], completed)
            self.module.database.session.expire_all()
            self.assertEqual(self.module.database.session.get(self.module.Task, task.id).completed, completed)

    def test_deletion_requires_confirmation_and_persists(self):
        task = self.task()
        task_id = task.id
        url = f'/tasks/{task_id}/delete'
        self.assertEqual(self.post(url).status_code, 400)
        page = self.post(url, json=False)
        self.assertEqual(page.status_code, 200)
        self.assertIn('name="confirm_delete" value="yes"', page.get_data(as_text=True))
        self.assertIsNotNone(self.module.database.session.get(self.module.Task, task_id))
        self.assertEqual(self.post(url, {'confirm_delete': 'yes'}).json['deleted_id'], task_id)
        self.assertIsNone(self.module.database.session.get(self.module.Task, task_id))

    def test_html_redirects_remain(self):
        self.assertEqual(self.post('/tasks', {'title': 'Fallback'}, False).status_code, 303)
        task = self.task()
        self.assertEqual(self.post(f'/tasks/{task.id}/toggle', json=False).status_code, 303)
        self.assertEqual(self.post(f'/tasks/{task.id}/delete', {'confirm_delete': 'yes'}, False).status_code, 303)

    def test_expired_missing_and_unavailable_sessions(self):
        m = self.module
        task = self.task()
        paths = ('/tasks', f'/tasks/{task.id}/toggle', f'/tasks/{task.id}/delete')
        m.redis_client.get.return_value = 'another-user'
        for path in paths:
            self.assertEqual(self.post(path, {'title': 'Blocked', 'confirm_delete': 'yes'}).status_code, 401)
        self.assertEqual(self.post('/tasks', {'title': 'Blocked'}, False).status_code, 302)
        with self.client.session_transaction() as session:
            session.update(user_id=1, session_id='test-session', csrf_token='test-csrf')
        m.redis_client.get.side_effect = m.RedisError('test outage')
        self.assertEqual(self.post('/tasks', {'title': 'Blocked'}).status_code, 503)
        self.assertFalse(task.completed)


if __name__ == '__main__':
    unittest.main()
