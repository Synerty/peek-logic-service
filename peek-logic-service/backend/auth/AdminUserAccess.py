

class AdminUserAccess:
    """ Admin User Access
    This class stores the details about the user that are required by the
    elements and resources to be able to allow access.
    """

    def __init__(self):
        """
        Constructor
        """
        self.loggedIn = False
        self.username = 'noname'

    def __repr__(self):
        return str(dict(
            loggedIn=self.loggedIn,
            username=self.username,
        ))
