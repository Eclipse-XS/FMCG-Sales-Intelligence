class EDAError(Exception):
    """Base EDA domain error."""


class UnknownTaskError(EDAError): pass
class DatasetNotFoundError(EDAError): pass
class UnsupportedDatasetError(EDAError): pass
class RequiredColumnsError(EDAError): pass
class RunNotFoundError(EDAError): pass
class CorruptRunError(EDAError): pass
class IncompatibleRunsError(EDAError): pass
