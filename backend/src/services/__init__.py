"""Services package for background tasks and utilities."""

from .stats_service import StatsService, get_stats_service, init_stats_service

__all__ = ['StatsService', 'get_stats_service', 'init_stats_service']
