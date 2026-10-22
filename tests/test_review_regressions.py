# -*- coding: utf-8 -*-
"""Regressions in the imported Netflix browsing and playback changes."""
# pylint: disable=protected-access
import inspect
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from resources.lib.common import VideoId
from resources.lib.kodi import infolabels
from resources.lib.navigation import actions
from resources.lib.services.nfsession.directorybuilder import dir_builder, dir_path_requests
from resources.lib.services.playback import am_playback


class ReviewRegressionTests(unittest.TestCase):
    def test_long_season_contains_episodes_after_first_fifty(self):
        request = dir_path_requests.DirectoryPathRequests(Mock())
        nodes = [{'node': {'videoId': i, 'number': i, 'title': str(i)}} for i in range(1, 76)]
        request._post_graphql = Mock(side_effect=lambda name, variables, operation: {
            'videos': [{'number': 1, 'episodes': {'edges': nodes[:variables['count']]}}]})
        request._metadata_episodes_by_id = Mock(return_value={})
        request._metadata_show_title = Mock(return_value='Test show')
        result = request._req_episodes_graphql(SimpleNamespace(seasonid='100', tvshowid='200'))
        self.assertEqual(len(result.episodes), 75)
        self.assertIn('75', result.episodes)

    def test_capped_episode_response_triggers_paginated_fallback(self):
        request = dir_path_requests.DirectoryPathRequests(Mock())
        nodes = [{'node': {'videoId': i}} for i in range(1, 51)]
        request._post_graphql = Mock(return_value={
            'videos': [{'episodes': {'edges': nodes}}]})
        with self.assertRaisesRegex(ValueError, 'end of the season'):
            request._req_episodes_graphql(SimpleNamespace(seasonid='100', tvshowid='200'))
        self.assertEqual(request._post_graphql.call_count, 2)

    def test_search_preserves_cached_my_list_membership(self):
        member = VideoId(movieid='123')
        builder = dir_builder.DirectoryBuilder(Mock())
        builder.req_video_list_search = Mock(return_value=Mock())
        with patch.object(dir_builder, 'G') as globals_mock, \
                patch.object(dir_builder, 'build_video_listing') as build:
            globals_mock.CACHE.get.return_value = [member]
            inspect.unwrap(builder.get_video_list_search)(builder, [], {}, 'test', None)
            self.assertEqual(build.call_args.kwargs['mylist_items'], [member])

    def test_my_list_change_refreshes_actions_outside_my_list(self):
        action = actions.AddonActionExecutor({})
        with patch.object(actions, 'api'), patch.object(actions, 'sync_library'), \
                patch.object(actions.common, 'WndHomeProps') as props, \
                patch.object(actions.common, 'container_refresh') as refresh:
            props.__getitem__.return_value = 'search'
            for operation in ('add', 'remove'):
                with self.subTest(operation=operation):
                    refresh.reset_mock()
                    inspect.unwrap(action.my_list)(action, VideoId(movieid='123'), ['my_list', operation])
                    refresh.assert_called_once_with()

    def test_partial_rewatch_keeps_resume_after_automatic_completion(self):
        manager = am_playback.AMPlayback()
        manager.videoid = VideoId(movieid='123')
        item = Mock()
        with patch.object(am_playback, 'G') as globals_mock, \
                patch.object(infolabels, 'G', globals_mock):
            globals_mock.SHARED_DB.get_watched_status.return_value = None
            globals_mock.SHARED_DB.set_watched_status.side_effect = lambda *args: setattr(
                globals_mock.SHARED_DB.get_watched_status, 'return_value', True)
            manager.on_playback_stopped({'nf_is_ads_stream': False, 'percentage': 99, 'current_pts': 990})
            globals_mock.CACHE.get.return_value = 120
            infolabels.set_watched_status(item, {
                'summary': {'value': {'id': 123}}, 'runtime': {'value': 1000}},
                {'set_watched_status': True, 'active_profile_guid': 'test'})
            item.setProperty.assert_any_call('ResumeTime', '120')
            globals_mock.SHARED_DB.set_watched_status.assert_not_called()


if __name__ == '__main__':
    unittest.main()
