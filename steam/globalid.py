import sys
from datetime import datetime, timedelta

if sys.version_info < (3,):
    intBase = long
else:
    intBase = int


class GlobalID(intBase):
    """
    Represents a globally unique identifier within the Steam network.
    Guaranteed to be unique across all racks and servers for a given Steam universe.
    """
    def __new__(cls, *args, **kwargs):
        if len(args) == 1:
            return super(GlobalID, cls).__new__(cls, *args)

        gid = GlobalID.new(*args, **kwargs)
        return super(GlobalID, cls).__new__(cls, gid)

    @staticmethod
    def new(sequence_count, start_time, process_id, box_id):
        """Make new GlobalID

        :param sequence_count: sequence count
        :type sequence_count: :class:`int`
        :param start_time: start date time of server (must be after 2005-01-01)
        :type start_time: :class:`str`, :class:`datetime`
        :param process_id: process id
        :type process_id: :class:`int`
        :param box_id: box id
        :type box_id: :class:`int`
        :return: Global ID integer
        :rtype: :class:`int`
        """
        if not isinstance(start_time, datetime):
            start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        start_time_seconds = int((start_time - datetime(2005, 1, 1)).total_seconds())

        return (box_id << 54) | (process_id << 50) | (start_time_seconds << 20) | sequence_count

    def __init__(self, *args, **kwargs):
        pass

    def __repr__(self):
        return "%s(sequence_count=%s, start_time=%s, process_id=%s, box_id=%s)" % (
            self.__class__.__name__,
            self.sequence_count,
            repr(str(self.start_time)),
            self.process_id,
            self.box_id,
            )

    @property
    def sequence_count(self):
        """
        :return: sequence count for GID
        :rtype: :class:`int`
        """
        return self & 0xFFFFF

    @property
    def start_time_seconds(self):
        """
        :return: seconds since 2005-01-01
        :rtype: :class:`int`
        """
        return (self >> 20) & 0x3FFFFFFF

    @property
    def start_time(self):
        """
        :return: start time of the server that generated this GID
        :rtype: :class:`datetime`
        """
        return datetime(2005, 1, 1) + timedelta(seconds=self.start_time_seconds)

    @property
    def process_id(self):
        """
        :return: process id of server
        :rtype: :class:`int`
        """
        return (self >> 50) & 0xF

    @property
    def box_id(self):
        """
        :return: box id of server
        :rtype: :class:`int`
        """
        return (self >> 54) & 0x3FF
