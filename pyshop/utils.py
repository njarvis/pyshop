def running_threads():
    """ Currently running threads

    :returns: list of running thread information
    :rtype: list of str

    """
    import threading

    threads = []
    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is main_thread:
            continue
        threads.append('#{}: {}: {}'.format(len(threads) + 1, t.getName(), t))
    return threads


def loggers():
    """ Currently configured loggers

    :returns: list of configured loggers
    :rtype: list of Logger objects

    """
    import logging

    root = logging.root
    existing = root.manager.loggerDict.keys()
    return [logging.getLogger(name) for name in existing]
