PEP 03: Better logging
======================

:state: draft


Goals
-----

* chomp latest \n from meuh.api handler


Example message
---------------

::

    {
        "status": "Downloading",
        "progressDetail": {
            "current": 14050508,
            "total": 90040320,
            "start": 1421605705
        },
        "progress": "[=======\u003e                                           ] 14.05 MB/90.04 MB 2m47s",
        "id": "d0a18d3b84de"
    }
