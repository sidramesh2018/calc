import re
import django_rq

from semantic_version import Version
from django.http import JsonResponse
from django.db.migrations.executor import MigrationExecutor
from django.db import connections, DEFAULT_DB_ALIAS

from hourglass import __version__
from hourglass.site_utils import get_canonical_url


def parse_pg_version(pg_version):
    # pg_version should be an integer that looks like 90410
    # returns a semantic_version.Version
    result = re.match(r'(\d)(\d\d)(\d\d)', str(pg_version))
    return Version(f"{result[1]}.{int(result[2])}.{int(result[3])}")


def get_database_info(database=DEFAULT_DB_ALIAS):
    connection = connections[database]
    connection.prepare_database()
    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()
    is_synchronized = False if executor.migration_plan(targets) else True
    return {
        'is_synchronized': is_synchronized,
        'pg_version': str(parse_pg_version(connection.pg_version)),
    }


def healthcheck(request):
    canonical_url = get_canonical_url(request)
    request_url = request.build_absolute_uri()

    db_info = get_database_info()

    results = {
        'version': __version__,
        'postgres_version': db_info['pg_version'],
        'is_database_synchronized': db_info['is_synchronized'],
        'canonical_url': canonical_url,
        'request_url': request_url,
        'canonical_url_matches_request_url': canonical_url == request_url,
        'rq_jobs': len(django_rq.get_queue().jobs),
    }

    status_code = 200

    if not (results['is_database_synchronized'] and
            results['canonical_url_matches_request_url']):
        status_code = 500

    return JsonResponse(results, status=status_code)
