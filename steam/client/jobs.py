import logging
from gevent import event
from steam.util.events import EventEmitter
from steam.enums.emsg import EMsg

logger = logging.getLogger("JobManager")


class JobManager(EventEmitter):
    """
    Takes care of managing job messages
    """

    _max_ulong = (2**64)-2

    def __init__(self, client):
        """
        Takes an instance of SteamClient
        """

        self._client = client
        self._client.on(None, self._handle_event)
        self._jobid = 0
        self._jobs = {}

    def _handle_event(self, event, *args):
        if len(args) != 1:
            return

        message = args[0]

        if not isinstance(event, EMsg) and not self._jobs:
            return

        if message.proto:
            jobid = message.header.jobid_target
        else:
            jobid = message.header.targetJobID

        if jobid in self._jobs:
            logger.debug("Response for job: %d, %s" % (jobid, repr(message)))
            self._jobs.pop(jobid).set(message)

    def get_jobid(self):
        """
        Returns the next job id
        """
        self._jobid = (self._jobid + 1) % self._max_ulong
        return self._jobid

    def send(self, message):
        """
        Sends a message as job, and returns the job id
        """
        jobid = self.get_jobid()

        logger.debug("Sending job: %d, %s" % (jobid, repr(message)))

        if message.proto:
            message.header.jobid_source = jobid
        else:
            message.header.sourceJobID = jobid

        self._jobs[jobid] = event.AsyncResult()
        self._client.send(message)
        return jobid

    def wait_for(self, jobid, timeout=None):
        """
        Blocks waiting for specified job id
        """

        if jobid not in self._jobs:
            raise ValueError("Specified jobid doen't exist. Did you call send() to get one?")

        return self._jobs[jobid].get(True, timeout)
