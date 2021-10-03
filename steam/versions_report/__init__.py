
import sys

def versions_report():
    """Print a report of al dependacy versions, and environment"""

    from steam import __version__
    print("steam: {}".format(__version__))

    # dependecy versions
    print("\nDependencies:")

    import pkg_resources

    installed_pkgs = {pkg.project_name.lower(): pkg.version for pkg in pkg_resources.working_set}

    for dep in [
                "vdf",
                "protobuf",
                "requests",
                "cachetools",
                "gevent",
                "gevent-eventemitter",
                "pycryptodomex",
                "enum34",
                "win-inet-pton",
                ]:
        print("{:>20}: {}".format(dep, installed_pkgs.get(dep.lower(), "Not Installed")))

    # python runtime
    print("\nPython runtime:")
    print("          executable: %s" % sys.executable)
    print("             version: %s" % sys.version.replace('\n', ''))
    print("            platform: %s" % sys.platform)

    # system info
    import platform

    print("\nSystem info:")
    print("              system: %s" % platform.system())
    print("             machine: %s" % platform.machine())
    print("             release: %s" % platform.release())
    print("             version: %s" % platform.version())
