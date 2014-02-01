from django.db import connection, transaction

from analyzr.settings import LAMBDA


def execute(query):
    cursor = connection.cursor()

    cursor.execute(query)
    transaction.commit_unless_managed()

    return cursor


def newest_files(query, date=None):
    date_filter = ""

    if date:
        date_filter = "AND date <= '%s'" % date.isoformat()

    sql = """
        SELECT
            *
        FROM (
            SELECT
                *,
                GROUP_CONCAT(A.change_type ORDER BY A.date SEPARATOR "") AS change_history
            FROM
                ( %(query)s %(filter)s ) AS A
            WHERE
                A.change_type IS NOT NULL GROUP BY A.name
        ) AS B WHERE
            B.change_history NOT LIKE '%%D'
        ORDER BY
            B.date
    """ % { "query": query, "filter": date_filter }

    return sql.replace("%", "%%")


def mimetype_count(files):
    return """
        SELECT
            A.id,
            A.name,
            A.revision_id,
            A.mimetype,
            A.change_type,
            A.copy_of_id,
            COUNT(A.mimetype) AS count
        FROM
            ( %s ) AS A
        WHERE
            A.mimetype IS NOT NULL
        GROUP BY
            A.mimetype
    """ % files


def count_entries(query):
    return """
        SELECT
            A.id,
            COUNT(*) AS count
        FROM
            ( %s ) AS A
    """ % query


def delete(cls, query):
    return """
        DELETE FROM %s WHERE id IN ( SELECT * FROM (%s) AS TMP )
    """ % (cls._meta.db_table, query)


def reset(branch):
    query = """
        UPDATE
            parsr_revision
        SET
            measured = 0
        WHERE
            branch_id = %d
    """ % branch.id

    execute(query)


def squale(fields, group_by, query):
    def convert(field):
        return """
            -1 * LOG(
                %(lambda)s,
                SUM(
                    POW(
                        %(lambda)s,
                        -1 * A.%(field)s
                    )
                ) / COUNT(A.%(field)s)
            ) AS %(field)s_squale
        """ % {
            "field": field,
            "lambda": LAMBDA
        }

    select = ", ".join([convert(field) for field in fields])

    return """
        SELECT DISTINCT
            A.author_id,
            %(group_by)s,
            %(fields)s
        FROM
            ( %(query)s ) AS A
        GROUP BY
            A.%(group_by)s
    """ % {
        "fields": select,
        "query": query,
        "group_by": ", ".join(["A.%s" % group for group in group_by])
    }
