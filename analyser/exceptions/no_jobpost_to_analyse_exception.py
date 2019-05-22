class NoJobPostToAnalyseAvailable(Exception):
    def __init__(self, message=None):
        if message is None:
            super(NoJobPostToAnalyseAvailable, self).__init__("No new posts to analyse.")
        else:
            super(NoJobPostToAnalyseAvailable, self).__init__(message)
