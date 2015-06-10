import pykka

from mopidy import core

import logging
from datetime import datetime, timedelta
import urllib2

logger = logging.getLogger(__name__)


class DjazzFrontend(pykka.ThreadingActor, core.CoreListener):

    _idleSince = None
    _config = None

    def __init__(self, config, core):
        super(DjazzFrontend, self).__init__()
        self.core = core
        self._config = config['djazz']
        delta = timedelta(seconds=self._config['seconds_before_sleep'])
        self._idleSince = datetime.now() - delta

    # Your frontend implementation

    def playback_state_changed(self, old_state, new_state):
        if new_state == 'playing':

            if self._idleSince is not None:

                idleTime = datetime.now() - self._idleSince
                if idleTime.seconds > self._config['seconds_before_sleep']:
                    logger.info("Back from sleep")
                    djazzUrl = self._config['djazz_messaging_url']
                    try:
                        urllib2.urlopen(djazzUrl + 'mopidy-is-back-from-sleep').read()
                    except urllib2.HTTPError as e:
                        logger.warning("Error sending message 'back-from-sleep' to djazz (http %s)", e.code)

                self._idleSince = None

        else:

            self._idleSince = datetime.now()
