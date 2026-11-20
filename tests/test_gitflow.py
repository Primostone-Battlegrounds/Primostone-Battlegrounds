"""Branch routing contracts; fixtures are not platform or GitHub approval evidence."""
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import check_gitflow as flow

REPO = 'Primostone-Battlegrounds/Primostone-Battlegrounds'


def event(branch, target, body=''):
    return {'number': 99, 'pull_request': {
        'number': 99, 'body': body, 'head': {'ref': branch, 'sha': 'a' * 40,
        'repo': {'full_name': REPO}}, 'base': {'ref': target}}}


class Routes(unittest.TestCase):
    def route(self, branch, target, body=''):
        return flow.route('b' * 40, 'c' * 40, {'repository': REPO}, event(branch, target, body))

    def test_task_to_develop_uses_existing_authorization(self):
        self.assertFalse(self.route('task/g0-1', 'develop', 'Work-Item: g0-1'))

    def test_task_to_main_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'main accepts'):
            self.route('task/g0-1', 'main', 'Work-Item: g0-1')

    def test_maintenance_cannot_smuggle_task_identity(self):
        with self.assertRaisesRegex(ValueError, 'task/<id>'):
            self.route('chore/plan', 'develop', 'Work-Item: g0-1')

    def test_fork_task_is_rejected(self):
        data = event('task/g0-1', 'develop', 'Work-Item: g0-1')
        data['pull_request']['head']['repo']['full_name'] = 'fork/project'
        with self.assertRaisesRegex(ValueError, 'same repository'):
            flow.route('b', 'c', {'repository': REPO}, data)

    def test_release_requires_manifest_before_accepting(self):
        with patch.object(flow, 'run', return_value='{}'):
            with self.assertRaisesRegex(ValueError, 'release manifest'):
                self.route('release/0.0.1', 'main')

    def test_sync_is_only_current_main(self):
        with patch.object(flow, 'api', return_value={'object': {'sha': 'd' * 40}}):
            with self.assertRaisesRegex(ValueError, 'current main'):
                self.route('main', 'develop')

    def test_sync_accepts_exact_main_reference(self):
        with patch.object(flow, 'api', return_value={'object': {'sha': 'a' * 40}}):
            self.assertTrue(self.route('main', 'develop'))

    def test_unknown_integration_source_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'develop accepts'):
            self.route('feature/hidden', 'develop')

    def test_ai_review_can_use_same_github_account(self):
        review = {'commit_id': 'a' * 40, 'state': 'COMMENTED', 'body':
                  'AI-Review: PASS\nReviewed-Head: ' + 'a' * 40 +
                  '\nReviewer-Agent: subagent:review-1\nImplementer-Agent: opencode:session-1\n'
                  '\n## Findings\nNo unresolved findings.\n## Verification\nContract suite and diff inspected.'}
        self.assertTrue(flow.review_record(review, 'a' * 40))
        self.assertFalse(flow.review_record(review, 'b' * 40))
        review['body'] = review['body'].replace('subagent:review-1', 'opencode:session-1')
        self.assertFalse(flow.review_record(review, 'a' * 40))

    def test_native_approval_alone_is_not_ai_review(self):
        self.assertFalse(flow.review_record({'commit_id': 'a' * 40, 'state': 'APPROVED',
                                            'body': 'LGTM'}, 'a' * 40))


if __name__ == '__main__':
    unittest.main()
