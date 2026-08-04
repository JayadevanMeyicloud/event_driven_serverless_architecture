CREATE OR REPLACE PROCEDURE get_daily_report
(
    IN p_uploader_email TEXT,
    IN p_page INTEGER,
    IN p_limit INTEGER,
    INOUT uploaders_cursor REFCURSOR,
    INOUT summary_cursor REFCURSOR,
    INOUT filetype_cursor REFCURSOR
)
LANGUAGE plpgsql
AS $$
DECLARE

    v_offset INTEGER;

BEGIN

    v_offset := (p_page - 1) * p_limit;


    IF p_uploader_email IS NULL THEN

        OPEN uploaders_cursor FOR

        SELECT DISTINCT

            uploader_name,
            uploader_email

        FROM file_metadata

        WHERE uploaded_at >= CURRENT_DATE
          AND uploaded_at < CURRENT_DATE + INTERVAL '1 day'

        ORDER BY uploader_name, uploader_email

        LIMIT p_limit
        OFFSET v_offset;

    ELSE

        OPEN uploaders_cursor FOR

        SELECT
            NULL::TEXT AS uploader_name,
            NULL::TEXT AS uploader_email
        WHERE FALSE;

    END IF;


    IF p_uploader_email IS NOT NULL THEN

        OPEN summary_cursor FOR

        SELECT

            COUNT(*) AS total_files,

            COALESCE(SUM(file_size),0) AS total_storage,

            COUNT(*)
            FILTER
            (
                WHERE upload_status='SUCCESS'
            ) AS success_count,

            COUNT(*)
            FILTER
            (
                WHERE upload_status='FAILED'
            ) AS failed_count

        FROM file_metadata

        WHERE uploader_email = p_uploader_email

          AND uploaded_at >= CURRENT_DATE
          AND uploaded_at < CURRENT_DATE + INTERVAL '1 day';

    ELSE

        OPEN summary_cursor FOR

        SELECT

            0::BIGINT AS total_files,
            0::BIGINT AS total_storage,
            0::BIGINT AS success_count,
            0::BIGINT AS failed_count

        WHERE FALSE;

    END IF;


    IF p_uploader_email IS NOT NULL THEN

        OPEN filetype_cursor FOR

        SELECT

            file_type,

            COUNT(*) AS total_files

        FROM file_metadata

        WHERE uploader_email = p_uploader_email

          AND uploaded_at >= CURRENT_DATE
          AND uploaded_at < CURRENT_DATE + INTERVAL '1 day'

        GROUP BY file_type

        ORDER BY total_files DESC;

    ELSE

        OPEN filetype_cursor FOR

        SELECT

            NULL::TEXT AS file_type,
            0::BIGINT AS total_files

        WHERE FALSE;

    END IF;

END;
$$;