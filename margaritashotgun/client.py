import sys
import random
import logging
from margaritashotgun.cli import Cli
from margaritashotgun.exceptions import NoConfigurationError

# from .utility import utility
# from .worker import master as multiprocessing_master

logger = logging.getLogger(__name__)


class Client():
    """
    Client for parallel memory capture with LiME
    """

    def __init__(self, library=True, config=None):
        """
        :type library: bool
        :param library: Toggle for command line features
        :type config: dict
        :param config: Client configuration
        """

        self._cli = Cli()
        self.library = library
        if library is False:
            args = self._cli.parse_args(sys.argv[1:])
            self.config = self._cli.configure(arguments=args)
        else:
            if config is None:
                raise NoConfigurationError
            self.config = self._cli.configure(config=config)

    def run(self):
        print("running")

        # mutate configuration
        # TODO: refactor BIG TIME
        # util = utility(logger=self.logger)
        # multi_config, workers = util.transform(self.config)

        # instantiate multiprocessing master
        # try:
        #     master = multiprocessing_master(self.logger, multi_config,
        #                                     workers,
        #                                     interactive=self.interactive)

        # start worker threads
        #     master.start_workers()
        # except KeyboardInterrupt:
        #     sys.exit()
