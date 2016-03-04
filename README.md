Fernglas
========

Fernglas is a simple tool that checks the deployment status of a commit. It takes a string that identifies a commit (such as an issue tracker ticket number) and reports whether the corresponding commit is deployed on any of the defined servers.

Configuration
=============

Fernglas looks for configuration files named .fernglas.cfg in the user's home directory and in the current working directory. The configuration in the home directory should contain general settings like ssh options while a per-project file can hold server definitions specific to the project. The file format follows the ini-like syntax used by the standard python ConfigParser. An example:

[main]
servers = staging, production

[staging]
name = staging.example.com
versions-path = /path/to/versions.cfg

[production]
name = production.example.com
versions-path = /path/to/versions.cfg

The *servers* setting in the *main* section specifies what sections fernglas should check for server definitions. A minimal server definition consist of the server *name* and the *versions-path*. The latter must be a path to a buildout configuration file that contains the version pinning for the deployed egg.
