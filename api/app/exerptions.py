class LicenceExpiredError(Exception):
    def __init__(self):
        self.code = 509
    def __str__(self):
        return 'Your company licence was expired'