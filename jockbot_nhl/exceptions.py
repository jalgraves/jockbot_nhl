class NHLException(Exception):
    """Base class for NHL exceptions"""
    pass

class NHLTeamException(Exception):
    """Base class for NHLTeam Errors"""
    pass


class NHLPlayerError(Exception):
    """Base class for NHLTeam Errors"""
    pass

class NHLPlayerException(Exception):
    """Base clas for NHLPlayer errors"""
    pass

class NHLRequestException(NHLException):
    """Base class for NHL request exceptions"""
    pass
