import logging.config

class ColorFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[35m',
        'RESET': '\033[0m'
    }

    def format(self, record):
        formatted = super().format(record)
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        formatted = formatted.replace(record.levelname, f"{log_color}{record.levelname}{self.COLORS['RESET']}", 1)
        return formatted
