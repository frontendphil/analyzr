from django.db import connection, transaction


def execute(query):
    cursor = connection.cursor()

    cursor.execute(query)
    transaction.commit_unless_managed()


def newest_files(query):
    sql = """
        SELECT
            *
        FROM (
            SELECT
                *,
                group_concat(change_type, '') AS change_history
            FROM
                ( %s )
            WHERE
                change_type IS NOT NULL GROUP BY name
        ) WHERE
            change_history NOT LIKE 'D%%'
        ORDER BY
            date
    """ % query

    return sql.replace("%", "%%")

def median(query, field):
    return """
        SELECT
            AVG(%(field)s)
        FROM (
            SELECT
                %(field)s
            FROM
                %(query)s
            ORDER BY
                %(field)s
            LIMIT
                2 - (SELECT COUNT(*) FROM ( %(query)s )) % 2    -- odd 1, even 2
            OFFSET (
                SELECT
                    (COUNT(*) - 1) / 2
                FROM %(query)s
            )
        )
    """ % { "field": field, "query": query }

def mimetype_count(files):
    return """
        SELECT
            id,
            name,
            revision_id,
            mimetype,
            change_type,
            copy_of_id,
            COUNT(mimetype) AS count
        FROM
            ( %s )
        WHERE
            mimetype IS NOT NULL
        GROUP BY
            mimetype
    """ % files

def count_entries(query):
    return """
        SELECT
            id,
            COUNT(*) AS count
        FROM
            ( %s )
    """ % query

def delete(cls, query):
    return """
        DELETE FROM %s WHERE id IN ( %s )
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
