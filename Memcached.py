#!/usr/bin/env python

import socket
from contextlib import closing

class Memcached:
    def __init__(self, agent_config, checks_logger, raw_config):
        self.agent_config = agent_config
        self.checks_logger = checks_logger
        self.raw_config = raw_config

        self.host = 'localhost'
        self.port = '11211'

        if 'Memcached' in self.raw_config:
            config = self.raw_config['Memcached']
            for attr in ('host', 'port'):
                if attr in config:
                    setattr(self, attr, config[attr])

    def run(self):
        try:
            stats = {}
            with closing(socket.create_connection((self.host, self.port)).makefile('rb', 0)) as connection:
                connection.write("stats\r\n")
                for line in connection:
                    line = line.strip()
                    if line == "END":
                        break
                    else:
                        _, name, value = line.strip().split()
                        stats[name] = value
            if not len(stats):
                self.checks_logger.error("Memcached returned no stats, something's awry.")
                return {'running': False}
            else:
                stats.update(running=True)
                return stats
        except socket.error:
            self.checks_logger.exception("Memcached doesn't seem to be running, perhaps check your configuration?")
            return {'running': False}

if __name__ == '__main__':
    import logging
    print Memcached({}, logging, {}).run()
