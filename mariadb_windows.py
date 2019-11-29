import os
import platform
import sys

from winreg import *


class MariaDBConfiguration():
    lib_dirs = []
    libs = []
    version = []
    includes = []
    extra_objects = []
    extra_compile_args= []
    extra_link_args= []


def get_config(options):
    static= options["link_static"];
    mariadb_dir= options["install_dir"]
    required_version= "3.1.5"

    if not os.path.exists(mariadb_dir):
      try:
          mariadb_dir= os.environ["MARIADB_CC_INSTALL_DIR"]
          cc_version = ["", ""]
          cc_instdir = [mariadb_dir, ""]
          print("using environment configuration " + mariadb_dir)
      except KeyError:

          try:
              local_reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
              if platform.architecture()[0] == '32bit':
                  connector_key = OpenKey(local_reg,
                                          'SOFTWARE\\MariaDB Corporation\\MariaDB Connector C')
              else:
                  connector_key = OpenKey(local_reg,
                                          'SOFTWARE\\MariaDB Corporation\\MariaDB Connector C 64-bit',
                                          access=KEY_READ | KEY_WOW64_64KEY)
              cc_version = QueryValueEx(connector_key, "Version")
              if cc_version[0] < required_version:
                  print("MariaDB Connector/Python requires MariaDB Connector/C >= %s (found version: %s") \
                       % (required_version, cc_version[0])
                  sys.exit(2)
              mariadb_dir = QueryValueEx(connector_key, "InstallDir")

          except:
              print("Could not find InstallationDir of MariaDB Connector/C. "
                    "Please make sure MariaDB Connector/C is installed or specify the InstallationDir of "
                    "MariaDB Connector/C by setting the environment variable MARIADB_CC_INSTALL_DIR.")
              sys.exit(3)

    print("Found MariaDB Connector/C in '%s'" % mariadb_dir[0])
    cfg = MariaDBConfiguration()
    cfg.includes = [".\\include", mariadb_dir[0] + "\\include", mariadb_dir[0] + "\\include\\mysql"]
    cfg.lib_dirs = [mariadb_dir[0] + "\\lib"]
    cfg.libs = ["ws2_32", "advapi32", "kernel32", "shlwapi", "crypt32"]
    if static.lower() == "on":
        cfg.libs.append("mariadbclient")
    else:
        cfg.libs.append("libmariadb")
    cfg.extra_link_args= ["/NODEFAULTLIB:LIBCMT"]
    return cfg