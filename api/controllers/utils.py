def returns_json(method):
    def wrapper(self, *args, **kwargs):
        self.response.headers.add('Content-Type', 'application/json; charset=utf-8')
        return method(self, *args, **kwargs)
    return wrapper

def fallback_param_to_req(*parameters):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            for param in parameters:
                if param not in kwargs or kwargs[param] is None:
                    from_req = self.request.get(param, default_value=None)
                    if from_req is not None:
                        kwargs[param] = from_req

            return method(self, *args, **kwargs)
        return wrapper
    return decorator

def get_params_from_request(self, *params):
    return {param: self.request.get(param, default_value=None) for param in params}

def treat_empty_string_as_none(*parameters):
    def new_value(key, value):
        if key in parameters or len(parameters) is 0:
            return None if value is '' else value
        else:
            return value

    def decorator(method):
        def wrapper(self, *args, **kwargs):
            kwargs = {arg: new_value(arg, value) for arg, value in kwargs.items()}
            return method(self, *args, **kwargs)
        return wrapper
    return decorator

class IncorrectRequestContent(Exception):
    def __init__(self, *args, **kwargs):
        super(IncorrectRequestContent, self).__init__(*args, **kwargs)

def request_require(*parameters):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            for p in parameters:
                if self.request.get(p, default_value=None) is None:
                    raise IncorrectRequestContent('Parameter not found: {}'.format(p))
            return method(self, *args, **kwargs)
        return wrapper
    return decorator