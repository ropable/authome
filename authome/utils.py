import ast
import os
import urllib.parse

__version__ = '1.0.0'


def _convert(key,value, default=None, required=False, value_type=None,subvalue_type=None):
    if value_type is None:
        if default is not None:
            value_type = default.__class__
    if subvalue_type is None:
        if default and isinstance(default,(list,tuple)):
            subvalue_type = default[0].__class__

    if value_type is None:
        return value
    elif isinstance(value, value_type):
        return value
    elif issubclass(value_type, list):
        if isinstance(value, tuple):
            return list(value)
        else:
            value = str(value).strip()
            if not value:
                return []
            else:
                result = []
                for subvalue in value.split(","):
                    subvalue = subvalue.strip()
                    if not subvalue:
                        continue
                    try:
                        subvalue = ast.literal_eval(subvalue)
                    except (SyntaxError, ValueError):
                        pass
                    result.append(_convert(key,subvalue,required=True,value_type=subvalue_type))
                return result
    elif issubclass(value_type, tuple):
        if isinstance(value, list):
            return tuple(value)
        else:
            value = str(value).strip()
            if not value:
                return tuple()
            else:
                result = []
                for subvalue in value.split(","):
                    subvalue = subvalue.strip()
                    if not subvalue:
                        continue
                    try:
                        subvalue = ast.literal_eval(subvalue)
                    except (SyntaxError, ValueError):
                        pass
                    result.append(_convert(key,subvalue,required=True,value_type=subvalue_type))
                return tuple(result)
    elif issubclass(value_type, bool):
        value = str(value).strip()
        if not value:
            return False
        elif value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        else:
            raise Exception("'{}' is a boolean environment variable, only accept value 'true' ,'false' and '' with case insensitive, but the configured value is '{}'".format(key, value))
    elif issubclass(value_type, int):
        return int(value)
    elif issubclass(value_type, float):
        return float(value)
    else:
        raise Exception("'{0}' is a {1} environment variable, but {1} is not supported now".format(key, value_type))


def env(key, default=None, required=False, value_type=None,subvalue_type=None):
    """
    Retrieves environment variables and returns Python natives. The (optional)
    default will be returned if the environment variable does not exist.
    """
    try:
        value = os.environ[key]
        value = ast.literal_eval(value)
    except (SyntaxError, ValueError):
        pass
    except KeyError:
        if default is not None or not required:
            return default
        raise Exception("Missing required environment variable '%s'" % key)

    return _convert(key,value,default=default,required=required,value_type=value_type,subvalue_type=subvalue_type)


