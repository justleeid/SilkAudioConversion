"""
数据库音频查询导入服务
参考 development.md 第 7.3.1 节、PRD.md 第 2.1.8 节
"""
from abc import ABC, abstractmethod
from typing import Optional
import mysql.connector
from app.config import settings
from app.logger import logger


class BaseDatabaseAudioService(ABC):
    """数据库音频查询导入服务基类"""

    @abstractmethod
    def _get_connection(self):
        """获取数据库连接"""

    @abstractmethod
    def _build_count_sql(self, date_start_full: str, date_end_full: str,
                         keyword_pattern: Optional[str]) -> tuple[str, list]:
        """构建计数 SQL，子类负责方言及参数顺序"""

    @abstractmethod
    def _build_query_sql(self, date_start_full: str, date_end_full: str,
                         keyword_pattern: Optional[str], per_page: int,
                         offset: int) -> tuple[str, list]:
        """构建查询 SQL，子类负责方言及参数顺序"""

    @abstractmethod
    def _build_blob_sql(self) -> str:
        """构建获取 blob 的 SQL"""

    @abstractmethod
    def _build_batch_sql(self) -> str:
        """构建批量获取记录的 SQL（含 ORDER BY 以保证标题稳定）"""

    @abstractmethod
    def _build_delete_sql(self) -> tuple[str, str]:
        """构建删除音频及关联记录的 SQL (audio_sql, history_sql)"""

    @abstractmethod
    def _build_update_title_sql(self) -> str:
        """构建修改标题的 SQL"""

    def _format_records(self, rows: list[dict]) -> list[dict]:
        records = []
        for row in rows:
            created_at = row.get("created_at")
            if created_at:
                if hasattr(created_at, "strftime"):
                    created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    created_at = str(created_at)
            else:
                created_at = ""
            records.append({
                "audio_id": row["audio_id"],
                "title": row.get("title") or "(无标题)",
                "created_at": created_at,
                "size": row.get("size") or 0,
                "format": "WAV"
            })
        return records

    async def query_audio_records(
        self,
        date_start: str,
        date_end: str,
        keyword: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            date_start_full = f"{date_start} 00:00:00"
            date_end_full = f"{date_end} 23:59:59"
            keyword_pattern = f"%{keyword}%" if keyword else None
            offset = (page - 1) * per_page

            # 计数
            count_sql, count_params = self._build_count_sql(
                date_start_full, date_end_full, keyword_pattern
            )
            cursor.execute(count_sql, count_params)
            total = cursor.fetchone()[0]

            # 查询
            query_sql, query_params = self._build_query_sql(
                date_start_full, date_end_full, keyword_pattern, per_page, offset
            )
            cursor.execute(query_sql, query_params)
            columns = [desc[0] for desc in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

            records = self._format_records(rows)
            logger.info(f"查询数据库音频: total={total}, page={page}, 返回 {len(records)} 条")
            return {"total": total, "page": page, "per_page": per_page, "records": records}
        finally:
            cursor.close()
            conn.close()

    async def get_audio_blob(self, audio_id: str) -> bytes:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            sql = self._build_blob_sql()
            cursor.execute(sql, (audio_id,))
            result = cursor.fetchone()
            if not result or not result[0]:
                raise ValueError(f"音频 {audio_id} 不存在或内容为空")
            logger.info(f"获取音频 blob: {audio_id}, size={len(result[0])} bytes")
            return result[0]
        finally:
            cursor.close()
            conn.close()

    async def get_audio_records_batch(self, audio_ids: list[str]) -> list[dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            results = []
            sql = self._build_batch_sql()
            for audio_id in audio_ids:
                cursor.execute(sql, (audio_id,))
                row = cursor.fetchone()
                if row:
                    blob_data = row[2] if len(row) > 2 else row[1]
                    results.append({
                        "audio_id": row[0],
                        "title": row[1] or "(无标题)",
                        "blob": blob_data,
                        "size": len(blob_data) if blob_data else 0
                    })
            logger.info(f"批量获取音频: 请求 {len(audio_ids)}, 获取 {len(results)} 条")
            return results
        finally:
            cursor.close()
            conn.close()


    async def delete_audio_record(self, audio_id: str) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            audio_sql, history_sql = self._build_delete_sql()
            cursor.execute(history_sql, (audio_id,))
            cursor.execute(audio_sql, (audio_id,))
            conn.commit()
            affected = cursor.rowcount
            logger.info(f"删除音频记录: {audio_id}, 影响行数={affected}")
            return affected
        finally:
            cursor.close()
            conn.close()

    async def update_audio_title(self, audio_id: str, title: str) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            sql = self._build_update_title_sql()
            cursor.execute(sql, (title, audio_id))
            conn.commit()
            affected = cursor.rowcount
            logger.info(f"修改音频标题: {audio_id} -> {title}, 影响行数={affected}")
            return affected
        finally:
            cursor.close()
            conn.close()


class MySQLDatabaseAudioService(BaseDatabaseAudioService):
    """MySQL 数据库音频查询导入服务"""

    def _get_connection(self):
        return mysql.connector.connect(
            host=settings.db_audio_host,
            port=settings.db_audio_port,
            user=settings.db_audio_user,
            password=settings.db_audio_password,
            database=settings.db_audio_name,
            charset=settings.db_audio_charset
        )

    def _build_count_sql(self, date_start_full: str, date_end_full: str,
                         keyword_pattern: Optional[str]) -> tuple[str, list]:
        sql = f"""
            SELECT COUNT(*) as total
            FROM {settings.db_history_table} h
            JOIN {settings.db_audio_table} a ON h.audio_id = a.id
            WHERE h.chat_type = 2 AND h.created_at >= %s AND h.created_at <= %s
        """
        params = [date_start_full, date_end_full]
        if keyword_pattern:
            sql += " AND h.content LIKE %s"
            params.append(keyword_pattern)
        return sql, params

    def _build_query_sql(self, date_start_full: str, date_end_full: str,
                         keyword_pattern: Optional[str], per_page: int,
                         offset: int) -> tuple[str, list]:
        sql = f"""
            SELECT
                a.id as audio_id,
                SUBSTRING(h.content, 1, 50) as title,
                h.created_at,
                OCTET_LENGTH(a.audio) as size
            FROM {settings.db_history_table} h
            JOIN {settings.db_audio_table} a ON h.audio_id = a.id
            WHERE h.chat_type = 2 AND h.created_at >= %s AND h.created_at <= %s
        """
        params = [date_start_full, date_end_full]
        if keyword_pattern:
            sql += " AND h.content LIKE %s"
            params.append(keyword_pattern)
        sql += " ORDER BY h.created_at DESC LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        return sql, params

    def _build_blob_sql(self) -> str:
        return f"SELECT audio FROM {settings.db_audio_table} WHERE id = %s"

    def _build_batch_sql(self) -> str:
        return f"""
            SELECT
                a.id as audio_id,
                SUBSTRING(h.content, 1, 50) as title,
                a.audio as blob_data
            FROM {settings.db_audio_table} a
            LEFT JOIN {settings.db_history_table} h ON a.id = h.audio_id
            WHERE a.id = %s
            ORDER BY h.created_at DESC
            LIMIT 1
        """

    def _build_delete_sql(self) -> tuple[str, str]:
        return (
            f"DELETE FROM {settings.db_audio_table} WHERE id = %s",
            f"DELETE FROM {settings.db_history_table} WHERE audio_id = %s"
        )

    def _build_update_title_sql(self) -> str:
        return f"UPDATE {settings.db_history_table} SET content = %s WHERE audio_id = %s"


class SQLServerDatabaseAudioService(BaseDatabaseAudioService):
    """SQL Server 数据库音频查询导入服务"""

    def _table(self, name: str) -> str:
        s = settings.db_mssql_schema
        d = settings.db_mssql_name
        return f"{d}.{s}.{name}"

    def _get_connection(self):
        import pyodbc
        driver = settings.db_mssql_driver
        # allow driver names that may contain braces; ensure proper formatting
        conn_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={settings.db_mssql_host},{settings.db_mssql_port};"
            f"DATABASE={settings.db_mssql_name};"
            f"UID={settings.db_mssql_user};"
            f"PWD={settings.db_mssql_password}"
        )
        return pyodbc.connect(conn_str)

    def _build_count_sql(self, date_start_full: str, date_end_full: str,
                         keyword_pattern: Optional[str]) -> tuple[str, list]:
        ht = self._table(settings.db_mssql_history_table)
        at = self._table(settings.db_mssql_table)
        sql = f"""
            WITH filtered AS (
                SELECT
                    a.id,
                    h.created_at,
                    ROW_NUMBER() OVER (
                        PARTITION BY a.id
                        ORDER BY h.created_at DESC, h.id DESC
                    ) AS rn
                FROM {ht} h
                JOIN {at} a ON h.audio_id = a.id
                WHERE h.chat_type = 2 AND h.created_at >= ? AND h.created_at <= ?
                  AND a.is_deleted = 0
            )
            SELECT COUNT(*) as total
            FROM filtered
            WHERE rn = 1
        """
        params = [date_start_full, date_end_full]
        if keyword_pattern:
            sql = f"""
                WITH filtered AS (
                    SELECT
                        a.id,
                        h.created_at,
                        ROW_NUMBER() OVER (
                            PARTITION BY a.id
                            ORDER BY h.created_at DESC, h.id DESC
                        ) AS rn
                    FROM {ht} h
                    JOIN {at} a ON h.audio_id = a.id
                    WHERE h.chat_type = 2 AND h.created_at >= ? AND h.created_at <= ?
                      AND a.is_deleted = 0
                      AND h.content LIKE ?
                )
                SELECT COUNT(*) as total
                FROM filtered
                WHERE rn = 1
            """
            params.append(keyword_pattern)
        return sql, params

    def _build_query_sql(self, date_start_full: str, date_end_full: str,
                         keyword_pattern: Optional[str], per_page: int,
                         offset: int) -> tuple[str, list]:
        ht = self._table(settings.db_mssql_history_table)
        at = self._table(settings.db_mssql_table)
        sql = f"""
            WITH filtered AS (
                SELECT
                    a.id AS audio_id,
                    SUBSTRING(h.content, 1, 50) AS title,
                    h.created_at,
                    a.size,
                    ROW_NUMBER() OVER (
                        PARTITION BY a.id
                        ORDER BY h.created_at DESC, h.id DESC
                    ) AS rn
                FROM {ht} h
                JOIN {at} a ON h.audio_id = a.id
                WHERE h.chat_type = 2 AND h.created_at >= ? AND h.created_at <= ?
                  AND a.is_deleted = 0
            )
            SELECT
                audio_id,
                title,
                created_at,
                size
            FROM filtered
            WHERE rn = 1
        """
        params = [date_start_full, date_end_full]
        if keyword_pattern:
            sql = f"""
            WITH filtered AS (
                SELECT
                    a.id AS audio_id,
                    SUBSTRING(h.content, 1, 50) AS title,
                    h.created_at,
                    a.size,
                    ROW_NUMBER() OVER (
                        PARTITION BY a.id
                        ORDER BY h.created_at DESC, h.id DESC
                    ) AS rn
                FROM {ht} h
                JOIN {at} a ON h.audio_id = a.id
                WHERE h.chat_type = 2 AND h.created_at >= ? AND h.created_at <= ?
                  AND a.is_deleted = 0
                  AND h.content LIKE ?
            )
            SELECT
                audio_id,
                title,
                created_at,
                size
            FROM filtered
            WHERE rn = 1
            """
            params.append(keyword_pattern)
        sql += " ORDER BY created_at DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        params.extend([offset, per_page])
        return sql, params

    def _build_blob_sql(self) -> str:
        return f"SELECT audio FROM {self._table(settings.db_mssql_table)} WHERE id = ?"

    def _build_batch_sql(self) -> str:
        ht = self._table(settings.db_mssql_history_table)
        at = self._table(settings.db_mssql_table)
        return f"""
            SELECT TOP 1
                a.id as audio_id,
                SUBSTRING(h.content, 1, 50) as title,
                a.audio as blob_data
            FROM {at} a
            LEFT JOIN {ht} h ON a.id = h.audio_id
            WHERE a.id = ?
            ORDER BY h.created_at DESC
        """

    def _build_delete_sql(self) -> tuple[str, str]:
        at = self._table(settings.db_mssql_table)
        ht = self._table(settings.db_mssql_history_table)
        return (
            f"DELETE FROM {at} WHERE id = ?",
            f"DELETE FROM {ht} WHERE audio_id = ?"
        )

    def _build_update_title_sql(self) -> str:
        ht = self._table(settings.db_mssql_history_table)
        return f"UPDATE {ht} SET content = ? WHERE audio_id = ?"


def get_db_service(source: str) -> BaseDatabaseAudioService:
    if source == "mssql":
        return SQLServerDatabaseAudioService()
    return MySQLDatabaseAudioService()
