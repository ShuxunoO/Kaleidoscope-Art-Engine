
class NULL_File_Error(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message



class PercentageError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message





