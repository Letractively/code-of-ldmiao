#!/usr/bin/python


"""Simple YouTube.com API Client

This is a very simple wrapper aroud the YouTube.com REST API as
documented on http://youtube.com/dev_docs. You need to obtain a
developer key in order to use the API.

Author: Thomas Perl <thp@thpinfo.com>

Copyright (c) 2007, 2008 Thomas Perl

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, 
MA  02110-1301, USA.

Example usage:

>>> c = YouTubeClient('your-dev-id')
>>>
>>> for video in c.list_by_user('your-username'):
>>>     v = c.get_details(video['id'])
>>>     print video['id']
>>>     print v['thumbnail_url']
>>>     print v['title']
>>>     print v['description']

"""

from xml.dom import minidom
from urllib2 import urlopen

class YouTubeClient(object):
    """Simple YouTube.com API Client

    See U{http://youtube.com/dev_docs} for more information. You need
    to get a B{Developer API Key} from U{http://youtube.com/my_profile_dev} 
    to use the YouTube API and pass it as string to the constructor.
    """

    REST_ENDPOINT = 'http://www.youtube.com/api2_rest'
    TIME_RANGES = ('day', 'week', 'month', 'all')
    CATEGORIES = {
            1: 'Films & Animation',
            2: 'Autos & Vehicles',
            23: 'Comedy',
            24: 'Entertainment',
            10: 'Music',
            25: 'News & Politics',
            22: 'People & Blogs',
            15: 'Pets & Animals',
            26: 'How-to & DIY',
            17: 'Sports',
            19: 'Travel & Places',
            20: 'Gadgets & Games',
    }

    def __init__(self, dev_id):
        self.dev_id = dev_id

    @staticmethod
    def xml_dom_get_text(node):
        """This method is used internally to get XML text data."""
        result = []
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE:
                result.append(child.data)
        return ''.join(result)

    def xml_dom_node_to_dict(self, node):
        """This method is used internally to turn an Element into a dict."""
        result = {} 
        for child in node.childNodes:
            if child.nodeType == child.ELEMENT_NODE:
                result[child.tagName] = self.xml_dom_get_text(child)
        return result

    def generate_url(self, method, commands):
        """Builds a request URL from given keyword arguments, adding the
        REST endpoint for the YouTube API and the developer key."""
        commands['dev_id'] = self.dev_id
        args = '&'.join(['%s=%s' % (k, commands[k]) for k in commands.keys()])
        return '%s?method=%s&%s' % (self.REST_ENDPOINT, method, args)

    def call(self, method, **kwargs):
        """This method is used internally to perform the
        method call and convert the response XML."""

        xmldata = urlopen(self.generate_url(method, kwargs)).read()

        doc = minidom.parseString(xmldata)
        response = doc.getElementsByTagName('ut_response')[0]

        if response.getAttribute('status') != 'ok':
            print 'YouTube API Error'
            return None
        
        video_details = response.getElementsByTagName('video_details')
        if len(video_details):
            return self.xml_dom_node_to_dict(video_details[0])

        user_profile = response.getElementsByTagName('user_profile')
        if len(user_profile):
            return self.xml_dom_node_to_dict(user_profile[0])

        result = []

        video_lists = response.getElementsByTagName('video_list')
        if len(video_lists):
            videos = video_lists[0].getElementsByTagName('video')
            for video in videos:
                result.append(self.xml_dom_node_to_dict(video))

        friend_lists = response.getElementsByTagName('friend_list')
        if len(friend_lists):
            friends = friend_lists[0].getElementsByTagName('friend')
            for friend in friends:
                result.append(self.xml_dom_node_to_dict(friend))

        return result

    def get_profile(self, user):
        """Retrieves the public parts of a user profile."""
        return self.call('youtube.users.get_profile', user=user)
    
    def list_favorite_videos(self, user):
        """Lists a user's favorite videos."""
        return self.call('youtube.users.list_favourite_videos', user=user)

    def list_friends(self, user, page=1, per_page=20):
        """Lists a user's friends."""
        return self.call('youtube.users.list_friends',
                         user=user, page=page, per_page=per_page)

    def get_details(self, video_id):
        """Displays the details for a video."""
        return self.call('youtube.videos.get_details', video_id=video_id)

    def list_by_tag(self, tag, page=1, per_page=20):
        """Lists all videos that have the specified tag"""
        return self.call('youtube.videos.list_by_tag',
                         tag=tag, page=page, per_page=per_page)

    def list_by_user(self, user, page=1, per_page=20):
        """Lists all videos that were uploaded by the specified user"""
        return self.call('youtube.videos.list_by_user',
                         user=user, page=page, per_page=per_page)

    def list_featured(self):
        """Lists the most recent 25 videos that have been
        featured on the front page of the YouTube site."""
        return self.call('youtube.videos.list_featured')

    def list_by_playlist(self, playlist_id, page=1, per_page=20):
        """Lists all videos in the specified playlist"""
        return self.call('youtube.videos.list_by_playlist',
                         id=playlist_id, page=page, per_page=per_page)

    def list_popular(self, time_range='all'):
        """Lists most popular videos in the specified time_range"""
        if not time_range in self.TIME_RANGES:
            return None

        return self.call('youtube.videos.list_popular', time_range=time_range)

    def list_by_category_and_tag(self, category_id, tag, page=1, per_page=20):
        """Lists all videos that have the specified category id and tag."""
        try:
            category_id = int(category_id)
        except TypeError:
            return None
        except ValueError:
            return None

        if not category_id in self.CATEGORIES.keys():
            return None

        return self.call('youtube.videos.list_by_category_and_tag',
                         category_id=category_id, tag=tag,
                         page=page, per_page=per_page)


