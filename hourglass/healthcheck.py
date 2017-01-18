from django.http import JsonResponse
from django.db.migrations.executor import MigrationExecutor
from django.db import connections, DEFAULT_DB_ALIAS
import django_rq

from hourglass import __version__


def is_database_synchronized(database=DEFAULT_DB_ALIAS):
    connection = connections[database]
    connection.prepare_database()
    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()
    return False if executor.migration_plan(targets) else True


def healthcheck(request):
    results = {
        'version': __version__,
        'is_database_synchronized': is_database_synchronized(),
        'rq_jobs': len(django_rq.get_queue().jobs),
    }

    status_code = 200

    if not results['is_database_synchronized']:
        status_code = 500

    return JsonResponse(results, status=status_code)
