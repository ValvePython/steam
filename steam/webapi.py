import requests


class WebAPI(object):
    """
    Steam Web API wrapper

    Interfaces and methods are populated upon init based on
    response of available such from the API.

    More: https://developer.valvesoftware.com/wiki/Steam_Web_API
    """

    def __init__(self, key, https=True):
        """
        Optain apikey at https://steamcommunity.com/dev/apikey
        """

        self.https = https
        self.key = key
        self.interfaces = []
        self.load_interfaces()

    def __repr__(self):
        return "%s(key=%s, https=%s)" % (
            self.__class__.__name__,
            repr(self.key),
            repr(self.https),
            )

    def load_interfaces(self):
        """
        Fetches the available interfaces from the API itself and then
        populates the name space under the instance
        """

        result = self._api_request(
            "GET",
            "ISteamWebAPIUtil/GetSupportedAPIList/v1/",
            )

        if result.get('apilist', {}).get('interfaces', None) is None:
            raise ValueError("Invalid response for GetSupportedAPIList")

        interfaces = result['apilist']['interfaces']
        if len(interfaces) == 0:
            raise ValueError("API returned not interfaces; probably using invalid key")

        # clear existing interface instances
        for interface in self.interfaces:
            delattr(self, interface.name)
        self.interfaces = []

        # create interface instances from response
        for interface in interfaces:
            obj = WebAPIInterface(interface, parent=self)
            self.interfaces.append(obj)
            setattr(self, obj.name, obj)

    def call(self, method_path, **kwargs):
        """
        Make an API call for specific method

        method_path is a str in the format of "INTERFACE.METHOD"
        """

        interface, method = method_path.split('.', 1)
        return getattr(getattr(self, interface), method)(**kwargs)

    @property
    def _url_base(self):
        return "%s://api.steampowered.com/" % ('https' if self.https else 'http')

    def _api_request(self, method, path, **kwargs):
        if method not in ('GET', 'POST'):
            raise NotImplemented("Unsupported method: %s" % self.method)

        # set the key for every request, unless it's already specified by the method
        if kwargs.get('params', {}).get('key', None) is None:
            if 'params' not in kwargs:
                kwargs['params'] = {}
            kwargs['params']['key'] = self.key

        # move params to data, if data is not specified for POST
        # simplifies code calling this method
        if method == 'POST' and 'data' not in kwargs:
            kwargs['data'] = kwargs['params']
            del kwargs['params']

        f = getattr(requests, method.lower())
        resp = f(self._url_base + path, **kwargs)

        if not resp.ok:
            raise requests.exceptions.HTTPError("%s %s" % (resp.status_code, resp.reason))

        return resp.json()

    def doc(self):
        doc = "Steam Web API - List of all interfaces\n\n"
        for interface in self.interfaces:
            doc += interface.doc()
        return doc


class WebAPIInterface(object):
    """
    Steam Web API Interface
    """

    def __init__(self, interface_dict, parent=None):
        self._parent = parent
        self.name = interface_dict['name']
        self.methods = []

        for method in interface_dict['methods']:
            obj = WebAPIMethod(method, parent=self)
            self.methods.append(obj)
            setattr(self, obj.name, obj)

    def __repr__(self):
        return "<%s %s with %s methods>" % (
            self.__class__.__name__,
            repr(self.name),
            repr(len(list(self))),
            )

    def __iter__(self):
        return iter(self.methods)

    @property
    def https(self):
        return self._parent.https

    def doc(self):
        doc = "%s\n%s\n" % (self.name, '-'*len(self.name))
        for method in self.methods:
            doc += "  %s\n" % method.doc().replace("\n", "\n  ")
        return doc


class WebAPIMethod(object):
    """
    Steam Web API Interface Method
    """

    def __init__(self, method_dict, parent=None):
        self._parent = parent
        self._dict = method_dict

        params = method_dict['parameters']
        self._dict['parameters'] = {}
        for param in params:
            # add property indicating param can be a list
            param['_array'] = param['name'].endswith('[0]')
            # fix name
            param['name'] = param['name'].rstrip('[0]')
            # turn params from a list to a dict
            self._dict['parameters'][param['name']] = param

    def __repr__(self):
        return "<%s %s for %s>" % (
            self.__class__.__name__,
            repr(self.name),
            repr(self._parent.name),
            )

    def __call__(self, **kwargs):
        unrecognized = set(kwargs.keys()).difference(set(self._dict['parameters'].keys() + ['key']))
        if unrecognized:
            raise ValueError("Unrecognized parameter %s" % repr(unrecognized.pop()))

        params = {}
        for param in self.parameters.values():
            name = param['name']
            islist = param['_array']
            optional = param['optional']

            # raise if we are missing a required parameter
            if not optional and name not in kwargs and name != 'key':
                raise ValueError("Method requires %s to be set" % repr(name))

            # populate params that will be passed to _api_request
            if name in kwargs:
                # some parameters can be an array, they need to be send as seperate field
                # the array index is append to the name (e.g. name[0], name[1] etc)
                if islist:
                    if not isinstance(kwargs[name], list):
                        raise ValueError("Expected %s to be a list, got %s" % (repr(name), repr(type(kwargs[name]))))

                    for idx, value in enumerate(kwargs[name]):
                        params['%s[%d]' % (name, idx)] = value
                else:
                    params[name] = kwargs[name]

        # make the request
        return self._api_request(
            self.method,
            "%s/%s/v%s/" % (self._parent.name, self.name, self.version),
            params=params,
            )

    @property
    def version(self):
        return self._dict['version']

    @property
    def method(self):
        return self._dict['httpmethod']

    @property
    def parameters(self):
        return self._dict['parameters']

    @property
    def _api_request(self):
        return self._parent._parent._api_request

    @property
    def name(self):
        return self._dict['name']

    @property
    def https(self):
        return self._parent.https

    def doc(self):
        doc = "%(name)s (version: %(version)s)\n" % self._dict

        if 'description' in self._dict:
            doc += "\n  %(description)s\n" % self._dict

        if len(self.parameters):
            doc += "  \n  Parameters:\n"

            for param in sorted(self.parameters.values(), key=lambda x: x['name']):
                doc += "    %s %s %s%s\n" % (
                    param['name'].ljust(25),
                    (param['type']+"[]").ljust(8) if param['_array'] else param['type'].ljust(8),
                    'optional' if param['optional'] else 'required',
                    ("\n      - " + param['description']) if 'description' in param and param['description'] else '',
                    )

        return doc
