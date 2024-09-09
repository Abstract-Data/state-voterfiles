# import logging
# from dataclasses import dataclass
# from logging.handlers import SysLogHandler
# from pathlib import Path
# from typing import ClassVar
#
# logfile_path = Path(__file__).parent.parent / 'logs' / 'campaign_finance.log'
#
# @dataclass
# class Logger:
#     """
#     A class that provides logging functionality.
#
#     Attributes:
#         module_name (str): The name of the module where the logger is used.
#         project_name (ClassVar[str]): The name of the project. Default is "vep-2024".
#         formatter (logging.Formatter): The formatter for the logger messages.
#         silent_error_format (logging.Formatter): The formatter for silent error messages.
#         __PAPERTRAIL_HOST (str): The host for the PaperTrail log management service.
#         __PAPERTRAIL_PORT (int): The port for the PaperTrail log management service.
#
#     Properties:
#         logger_name (str): The name of the logger, derived from the project name.
#
#     Methods:
#         info(message: str): Logs an informational message.
#         debug(message: str): Logs a debug message.
#         warning(message: str): Logs a warning message.
#         error(message: str): Logs an error message.
#         critical(message: str): Logs a critical message.
#         exception(message: str): Logs an exception message.
#         silent_error(message: str): Logs a silent error message.
#     """
#     module_name: str
#     project_name: ClassVar[str] = "vep-2024"
#     formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
#     silent_error_format = logging.Formatter('%(asctime)s  %(name)s  SILENT %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
#     __PAPERTRAIL_HOST = "logs4.papertrailapp.com"
#     __PAPERTRAIL_PORT = 33096
#
#     def __repr__(self):
#         return f"{self.module_name} Logger"
#
#     @property
#     def logger_name(self):
#         """
#         Returns the name of the logger, derived from the project name.
#
#         Returns:
#             str: The name of the logger.
#         """
#         return Path(self.project_name).stem
#
#     def __post_init__(self):
#         self.logger = logging.Logger(f"{self.logger_name}@{self.module_name}")
#         self.logger.setLevel(level=logging.DEBUG)
#
#         # PaperTrail Logging Settings
#         # remote_handler = SysLogHandler(address=(self.__PAPERTRAIL_HOST, self.__PAPERTRAIL_PORT))
#         # remote_handler.setFormatter(self.formatter)
#
#         # Local Timed Logging Settings
#         timed_logfile = logging.handlers.TimedRotatingFileHandler(logfile_path, when='D', interval=7)
#         timed_logfile.setFormatter(self.formatter)
#
#         # Console Logging Settings
#         console_handler = logging.StreamHandler()
#         console_handler.setFormatter(self.formatter)
#
#         # Console-Silent Logging Settings
#         # silent_error_handler = remote_handler
#         # silent_error_handler.setFormatter(self.silent_error_format)
#
#         silent_error_local_handler = timed_logfile
#         self.error_logger = logging.Logger(f"{self.logger_name}@{self.module_name}")
#         self.error_logger.setLevel(level=logging.ERROR)
#         # self.error_logger.addHandler(silent_error_handler)
#         self.error_logger.addHandler(silent_error_local_handler)
#
#         # self.logger.addHandler(remote_handler)
#         self.logger.addHandler(timed_logfile)
#         self.logger.addHandler(console_handler)
#
#     def info(self, message):
#         """
#         Logs an informational message.
#
#         Args:
#             message (str): The message to log.
#         """
#         self.logger.info(message)
#
#     def debug(self, message):
#         """
#         Logs a debug message.
#
#         Args:
#             message (str): The message to log.
#         """
#         self.logger.debug(message)
#
#     def warning(self, message):
#         """
#         Logs a warning message.
#
#         Args:
#             message (str): The message to log.
#         """
#         self.logger.warning(message)
#
#     def error(self, message):
#         """
#         Logs an error message.
#
#         Args:
#             message (str): The message to log.
#         """
#         self.logger.error(message)
#
#     def critical(self, message):
#         """
#         Logs a critical message.
#
#         Args:
#             message (str): The message to log.
#         """
#         self.logger.critical(message)
#
#     def exception(self, message):
#         """
#         Logs an exception message.
#
#         Args:
#             message (str): The message to log.
#         """
#         self.logger.exception(message)
#
#     def silent_error(self, message):
#         """
#         Logs a silent error message.
#
#         Args:
#             message (str): The message to log.
#         """
#         self.error_logger.error(message)
