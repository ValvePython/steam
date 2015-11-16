from __future__ import print_function
import requests

DEFAULT_PARAMS = {
    # api parameters
    'key': None,
    'format': 'json',
    # internal
    'https': True,
    'http_timeout': 30,
    'raw': False,
}


def webapi_request(path, method='GET', caller=None, params={}):
    """
    Low level function for calling Steam's WebAPI
    """
    if method not in ('GET', 'POST'):
        raise NotImplemented("HTTP method: %s" % repr(self.method))

    onetime = {}
    for param in DEFAULT_PARAMS:
        params[param] = onetime[param] = params.get(param,
                                                    DEFAULT_PARAMS[param],
                                                    )
    path = "%s://api.steampowered.com/%s" % ('https' if params.get('https', True) else 'http',
                                             path)
    del params['raw']
    del params['https']
    del params['http_timeout']

    if onetime['format'] not in ('json', 'vdf', 'xml'):
        raise ValueError("Expected format to be json,vdf or xml; got %s" % onetime['format'])

    # move params to data, if data is not specified for POST
    # simplifies code calling this method
    kwargs = {'params': params} if method == "GET" else {'data': params}

    f = getattr(requests, method.lower())
    resp = f(path, stream=False, timeout=onetime['http_timeout'], **kwargs)

    if caller is not None:
        caller.last_response = resp

    if not resp.ok:
        raise requests.exceptions.HTTPError("%s %s" % (resp.status_code, resp.reason))

    if onetime['raw']:
        return resp.content

    if onetime['format'] == 'json':
        return resp.json()
    elif onetime['format'] == 'xml':
        import lxml.etree
        return lxml.etree.parse(resp.raw)
    elif onetime['format'] == 'vdf':
        import vdf
        return vdf.loads(resp.text)


class WebAPI(object):
    """
    Steam Web API wrapper

    Interfaces and methods are populated upon init based on
    response of available such from the API.

    More: https://developer.valvesoftware.com/wiki/Steam_Web_API
    """

    def __init__(self, key, format='json', raw=False, https=True, http_timeout=30, auto_load_interfaces=True):
        """
        Optain apikey at https://steamcommunity.com/dev/apikey

        key                   - apikey
        format                - output format (json, vdf, xml)
        raw                   - whenver to deserialize the response
        https                 - whenever to use https or not
        auto_load_interfaces  - should we load interfaces upon initialization

        These can be specified per method call for one off calls
        """

        self.key = key
        self.format = format
        self.raw = raw
        self.https = https
        self.http_timeout = http_timeout
        self.interfaces = []

        if auto_load_interfaces:
            self.load_interfaces(self.fetch_interfaces())

    def __repr__(self):
        return "%s(key=%s, https=%s)" % (
            self.__class__.__name__,
            repr(self.key),
            repr(self.https),
            )

    def fetch_interfaces(self):
        """
        Returns a dict with the response from GetSupportedAPIList

        This is then feeded into WebAPI.load_interfaces(reponse)
        The reponse could be cached/save and used to load interfaces
        """
        return webapi_request(
            "ISteamWebAPIUtil/GetSupportedAPIList/v1/",
            method="GET",
            caller=None,
            params={'format': 'json',
                    'key': self.key,
                    },
            )

    def load_interfaces(self, interfaces_dict):
        """
        Populates the namespace under the instance
        """
        if interfaces_dict.get('apilist', {}).get('interfaces', None) is None:
            raise ValueError("Invalid response for GetSupportedAPIList")

        interfaces = interfaces_dict['apilist']['interfaces']
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


    def doc(self):
        print(self.__doc__)

    @property
    def __doc__(self):
        doc = "Steam Web API - List of all interfaces\n\n"
        for interface in self.interfaces:
            doc += interface.__doc__
        return doc


class WebAPIInterface(object):
    """
    Steam Web API Interface
    """

    def __init__(self, interface_dict, parent):
        self._parent = parent
        self.name = interface_dict['name']
        self.methods = []

        for method in interface_dict['methods']:
            obj = WebAPIMethod(method, parent=self)
            self.methods.append(obj)

            # map the method name as attribute including version
            setattr(self, "%s_v%d" % (obj.name, obj.version), obj)

            # without version, but th refernce of latest version
            current_obj = getattr(self, obj.name, None)
            if current_obj is None or current_obj.version < obj.version:
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
    def key(self):
        return self._parent.key

    @property
    def https(self):
        return self._parent.https

    @property
    def http_timeout(self):
        return self._parent.http_timeout

    @property
    def format(self):
        return self._parent.format

    @property
    def raw(self):
        return self._parent.raw

    def doc(self):
        print(self.__doc__)

    @property
    def __doc__(self):
        doc = "%s\n%s\n" % (self.name, '-'*len(self.name))
        for method in self.methods:
            doc += "  %s\n" % method.__doc__.replace("\n", "\n  ")
        return doc


class WebAPIMethod(object):
    """
    Steam Web API Interface Method
    """

    def __init__(self, method_dict, parent):
        self.last_response = None
        self._parent = parent
        self._dict = method_dict

        params = method_dict['parameters']
        self._dict['parameters'] = {}
        for param in params:
            # add property indicating param can be a list
            param['_array'] = param['name'].endswith('[0]')
            # remove array suffix
            if param['_array']:
                param['name'] = param['name'][:-3]
            # turn params from a list to a dict
            self._dict['parameters'][param['name']] = param

    def __repr__(self):
        return "<%s %s>" % (
            self.__class__.__name__,
            repr("%s.%s_v%d" % (
                self._parent.name,
                self.name,
                self.version,
                )),
            )

    def __call__(self, **kwargs):
        possible_kwargs = set(self._dict['parameters'].keys()) | set(DEFAULT_PARAMS.keys())
        unrecognized = set(kwargs.keys()).difference(possible_kwargs)
        if unrecognized:
            raise ValueError("Unrecognized parameter %s" % repr(unrecognized.pop()))

        params = {}
        # process special case kwargs
        for param in DEFAULT_PARAMS.keys():
            if param in kwargs:
                params[param] = kwargs[param]
                del kwargs[param]
            else:
                params[param] = getattr(self._parent, param)

        # process method parameters
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
                        raise ValueError("Expected %s to be a list, got %s" % (
                            repr(name),
                            repr(type(kwargs[name])))
                            )

                    for idx, value in enumerate(kwargs[name]):
                        params['%s[%d]' % (name, idx)] = value
                else:
                    params[name] = kwargs[name]

        # make the request
        return webapi_request(
            "%s/%s/v%s/" % (self._parent.name, self.name, self.version),
            method=self.method,
            caller=self,
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
    def name(self):
        return self._dict['name']

    def doc(self):
        print(self.__doc__)

    @property
    def __doc__(self):
        doc = "%(httpmethod)s %(name)s (v%(version)04d)\n" % self._dict

        if 'description' in self._dict:
            doc += "\n  %(description)s\n" % self._dict

        if len(self.parameters):
            doc += "  \n  Parameters:\n"

            for param in sorted(self.parameters.values(), key=lambda x: x['name']):
                doc += "    %s %s %s%s\n" % (
                    param['name'].ljust(25),
                    ((param['type']+"[]") if param['_array'] else
                     param['type']
                     ).ljust(8),
                    'optional' if param['optional'] else 'required',
                    (("\n      - " + param['description'])
                     if 'description' in param and param['description'] else ''
                     ),
                    )

        return doc
