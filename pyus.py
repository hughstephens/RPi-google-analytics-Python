#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
This module is a library to build anonymous usage statistics, with `Google analytics`_,
using the `Google measurement protocol`_.

.. _`Google analytics`: http://www.google.com/analytics/
.. _`Google measurement protocol`: https://developers.google.com/analytics/devguides/collection/protocol/v1/
"""
# this should work both on Python 2 and Python 3
import threading

try:
    # exists only in Python 3
    import urllib.request as urlbib
    from urllib.parse import urlencode
    import queue
except ImportError:
    # Python 2
    import urllib2 as urlbib
    from urllib import urlencode
    import Queue as queue

__author__ = "Régis Décamps"
__license__ = """Copyright 2012 Régis Décamps

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
__version__ = 0.3

# List of complementary arguments that can be used in keyword arguments.
# The key can be used in methods that accept kwargs.
# For instance::
#     tracker = AppTracker(APP_NAME, TRACKING_ID, CLIENT_ID, language='fr')

FIELDNAME_TO_PARAM = {
    "language": 'ul',
    "anonymizeIp": 'aip',
    "encoding": 'de'
}

# TODO make this abstract
class AbstractTracker(object):
    """
    The tracker represents a tracking session for Google analytics.

    This is an abstract class, you should use :class:`AppTracker` instead.

    :param tracking_id:  You must provide your own `Tracking ID`_ / Web property / Property ID
    :type tracking_id: string of the form UA-XXXX-Y
    :param client_id: The client ID identifies a particular user and device instance. It must be anonymous -- it must not be the device ID / firmware number of the device. You should generate a random Client ID for each install (see `random_uuid()`) and store in the application settings.
    :type client_id: `string` in the form of a RFC4122 UUID, eg 35009a79-1a05-49d7-b876-2b884d0f825b

    Keyword arguments can be:

    * `language`: (`str`)  user language, as `ISO 639-1`_ code.
    * `anonymizeIp`: (`str`) When present, the IP address of the sender will be anonymized.
    * `encoding`: (`str`) The character set used to encode the page / document.

    .. _`Tracking ID`: http://support.google.com/analytics/bin/answer.py?answer=1032385
    .. _`ISO 639-1`:http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
    """
    # Google analytics API point
    GA_URL = 'http://www.google-analytics.com/collect'
    # Google analytics API version
    GA_VERSION = 1
    ENCODING = 'utf-8'

    def __init__(self, tracking_id, client_id=None, **kwargs):
        self.params = dict()
        self.params['tid'] = tracking_id
        if client_id is None:
            client_id = random_uuid()
        self.params['cid'] = client_id
        self.params['v'] = AbstractTracker.GA_VERSION

        for k in kwargs:
            if k in FIELDNAME_TO_PARAM:
                self.params[FIELDNAME_TO_PARAM[k]] = kwargs[k]

        self.post_queue = queue.Queue()
        # spawn a new thread for HTTP requests
        thread = threading.Thread(target=self._http_post_worker)
        # the entire Python program exits when only daemon threads are left. 
        # Daemon threads are abruptly stopped at shutdown, but I don't care for tracking.
        thread.daemon=True
        thread.start()


    def _track(self, hit_type, params=None):
        """
        Tracking method, called by subclasses.

        :param hit_type: hit type, should be provided by a subclass method.
        :param prams: A dict of other query parameters, should be provided by the subclass method.
        """
        http_params = dict()
        http_params.update(self.params)
        http_params['t'] = hit_type
        if params is not None:
            http_params.update(params)

        self.post_queue.put(http_params)

    def _http_post_worker(self):
        while True:
            params = self.post_queue.get(block=True)
            print("Params:",params)
            data = urlencode(params)
            print("data:",data)
            request_url = AbstractTracker.GA_URL + '?' + data
            print("Request1:",request_url)
            # adding charset parameter to the Content-Type header.
            response = urlbib.urlopen(request_url)
            print(response.read())
            print("Response:",response)
            print("done")
            # TODO handle response?
            


class AppTracker(AbstractTracker):
    """
    A Google analytics tracker for mobile or desktop applications.

    It provides methods to track screen view (see :func:`track_screen`) and events (see :func:`track_event`)
    within the application.

    :param app_name: The application name
    :type app_name: string

    Keyword arguments can be:

    * `version`: version of the application. Default value: 1.
    """

    def __init__(self, app_name, tracking_id, client_id=None, **kwargs):
        super(AppTracker, self).__init__(tracking_id, client_id, **kwargs)

    def track_event(self, category, action, label=None, value=-1, params=None):
        """
        Track an event within the application.

        :param category:  a category is a name that you supply as a way to group objects that you want to track. The term Category appears in the reporting interface as Top Categories in the Events Overview page.
        :param action: Typically, you will use the action parameter to name the type of event or interaction you want to track for a particular web object. For example, with a single "Videos" category, you can track a number of specific events with this parameter, such as play, stop, pause. You can supply any string for the action parameter. In some situations, the actual event or action name is not as meaningful, so you might use the action parameter to track other elements. For example, if you want to track page downloads, you could provide the document file type as the action parameter for the download event.
        :param label: With labels, you can provide additional information for events that you want to track, such as the movie title in the video example
        :param value: The report displays the total and average value for events. You can use this to track time, but there is also track_user_timing() for tat purpose.
        :type value: `int`
        """
        if params is None:
            params = dict()
        params['ec'] = category
        params['ea'] = action
        if label is not None:
            params['el'] = label
        if value > -1:
            params['ev'] = value
        self._track('event', params)

    def track_user_timing(self, category, variable, duration, label=None, params=None):
        """
        :param category: Specifies the user timing category.
        :param variable: Specifies the user timing variable, the name of the action of the resource being tracked.
        :param duration: Specifies the user timing value. the number of milliseconds in elapsed time.
        :type duration: `int` value in milliseconds
        :param label: add flexibility in visualizing user timings in the reports. Labels can also be used to focus on different sub experiments for the same category and variable combination.
        """
        if params is None:
            params = dict()
        params['utc'] = category
        params['utv'] = variable
        params['utt'] = duration
        if label is None:
            label = category + '.' + variable
        params['utl'] = label
        self._track('timing', params)


def random_uuid():
    """
    Generates a random UUID, based on the host ID and current time, as defined per RFC 4122 uuid1.

    :return: a UUID
    :type: `str`
    """
    import uuid

    u = uuid.uuid1()
    return str(u)
