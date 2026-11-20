"""Branch routing contracts; fixtures are not platform or GitHub approval evidence."""
import sys
from pathlib import Path
import unittest
import copy
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import check_gitflow as flow
import check_bootstrap as bootstrap

REPO = 'Primostone-Battlegrounds/Primostone-Battlegrounds'


def event(branch, target, body=''):
    return {'number': 99, 'pull_request': {
        'number': 99, 'body': body, 'user': {'login': 'actor'}, 'head': {'ref': branch, 'sha': 'a' * 40,
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

    def test_release_correction_cannot_change_task_authority(self):
        data = event('chore/release-fix-1', 'release/0.0.1')
        with patch.object(bootstrap, 'run', side_effect=['b\n' + 'a' * 40,
                  'backlog/tasks/m0-1 - task.md\0src/unowned.lua\0']), \
                patch.object(bootstrap, 'verify_merged_gate') as gate, \
                patch.object(bootstrap, 'changes', return_value=set()), \
                patch.object(bootstrap, 'ai_review'):
            with self.assertRaisesRegex(ValueError, 'freeze task authority'):
                bootstrap.validate_pr(None, 'b', 'c', {'tasks': {}}, {'repository': REPO}, data)
            gate.assert_not_called()

    def test_metadata_only_downstream_start_requires_main_promotion(self):
        old = {f'g0-{i}': {'status': 'Done', 'milestone': 'G0'} for i in range(1, 8)}
        old['m0-1'] = {'status': 'To Do', 'milestone': 'M0', 'modified_files': []}
        tasks = copy.deepcopy(old)
        tasks['m0-1']['status'] = 'In Progress'
        with patch.object(bootstrap, 'run', side_effect=['b\n' + 'a' * 40, 'config',
                         'b\n' + 'a' * 40]), \
                patch.object(bootstrap, 'changes', return_value={'backlog/tasks/m0-1 - task.md'}), \
                patch.object(bootstrap, 'read_blob', return_value='{"work": {}}'), \
                patch.object(bootstrap, 'local_corpus', return_value={'tasks': old}), \
                patch.object(bootstrap, 'authorize'), patch.object(bootstrap, 'ai_review'), \
                patch.object(bootstrap, 'verify_merged_gate', side_effect=ValueError('main promotion absent')):
            with self.assertRaisesRegex(ValueError, 'main promotion absent'):
                bootstrap.validate_pr(None, 'b', 'c', {'tasks': tasks}, {'repository': REPO},
                                      event('task/m0-1', 'develop', 'Work-Item: m0-1'))

    def test_actual_chinese_task_filename_cannot_bypass_release_freeze(self):
        path = 'backlog/tasks/m0-1 - 规则值类型与状态工厂.md'

        def git_output(*argv):
            if 'rev-parse' in argv:
                return 'b\n' + 'a' * 40
            # Exercise Git's real quoted/raw filename serialization, not a hand-written escape.
            return flow.run('git', '-c', 'core.quotePath=true', 'ls-files',
                            *(['-z'] if '-z' in argv else []), '--', path)

        with patch.object(bootstrap, 'run', side_effect=git_output), \
                patch.object(bootstrap, 'verify_merged_gate'), \
                patch.object(bootstrap, 'changes', return_value=set()), \
                patch.object(bootstrap, 'ai_review'):
            with self.assertRaisesRegex(ValueError, 'freeze task authority'):
                bootstrap.validate_pr(None, 'b', 'c', {'tasks': {}}, {'repository': REPO},
                                      event('chore/release-fix-1', 'release/0.0.1'))


if __name__ == '__main__':
    unittest.main()
