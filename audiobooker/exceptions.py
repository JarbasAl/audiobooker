class AudioBookerException(Exception):
    pass


class UnknownBookIdException(AudioBookerException):
    pass


class UnknownGenreIdException(AudioBookerException):
    pass


class UnknownAuthorIdException(AudioBookerException):
    pass


class UnknownBookException(AudioBookerException):
    pass


class UnknownGenreException(AudioBookerException):
    pass


class UnknownAuthorException(AudioBookerException):
    pass


class ParseErrorException(AudioBookerException):
    pass


class UnknownRuntimeError(AudioBookerException):
    pass
