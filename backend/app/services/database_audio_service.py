"""
数据库音频查询导入服务
参考 development.md 第 7.3.1 节、PRD.md 第 2.1.8 节
"""
from typing import Optional
import mysql.connector
from app.config import settings
from app.logger import logger


class DatabaseAudioService:
    """数据库音频查询导入服务"""

    def __init__(self):
        self.host = settings.db_audio_host
        self.port = settings.db_audio_port
        self.user = settings.db_audio_user
        self.password = settings.db_audio_password
        self.database = settings.db_audio_name
        self.charset = settings.db_audio_charset
        self.audio_table = settings.db_audio_table
        self.history_table = settings.db_history_table

    def _get_connection(self):
        return mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset=self.charset
        )

    async def query_audio_records(
        self,
        date_start: str,
        date_end: str,
        keyword: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> dict:
        """
        查询数据库中的音频记录（仅 chat_type=2 的消息）

        Args:
            date_start: 开始日期 (YYYY-MM-DD)
            date_end: 结束日期 (YYYY-MM-DD)
            keyword: 按 title(content) 模糊搜索关键字
            page: 页码
            per_page: 每页条数

        Returns:
            { total, page, per_page, records: [...] }
        """
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            base_where = "h.chat_type = 2 AND h.created_at >= %s AND h.created_at <= %s"
            base_params = [f"{date_start} 00:00:00", f"{date_end} 23:59:59"]

            # 计算总数
            count_sql = f"""
                SELECT COUNT(*) as total
                FROM {self.history_table} h
                JOIN {self.audio_table} a ON h.audio_id = a.id
                WHERE {base_where}
            """
            count_params = list(base_params)
            if keyword:
                count_sql += " AND h.content LIKE %s"
                count_params.append(f"%{keyword}%")

            cursor.execute(count_sql, count_params)
            total = cursor.fetchone()["total"]

            # 查询记录
            query_sql = f"""
                SELECT
                    a.id as audio_id,
                    SUBSTRING(h.content, 1, 50) as title,
                    h.created_at,
                    OCTET_LENGTH(a.audio) as size
                FROM {self.history_table} h
                JOIN {self.audio_table} a ON h.audio_id = a.id
                WHERE {base_where}
            """
            query_params = list(base_params)

            if keyword:
                query_sql += " AND h.content LIKE %s"
                query_params.append(f"%{keyword}%")

            offset = (page - 1) * per_page
            query_sql += " ORDER BY h.created_at DESC LIMIT %s OFFSET %s"
            query_params.extend([per_page, offset])

            cursor.execute(query_sql, query_params)
            rows = cursor.fetchall()

            # 格式化记录
            records = []
            for row in rows:
                created_at = row["created_at"]
                if created_at:
                    created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    created_at = ""
                records.append({
                    "audio_id": row["audio_id"],
                    "title": row["title"] or "(无标题)",
                    "created_at": created_at,
                    "size": row["size"] or 0,
                    "format": "WAV"  # 当前数据库均为 WAV 格式
                })

            logger.info(f"查询数据库音频: total={total}, page={page}, 返回 {len(records)} 条")

            return {
                "total": total,
                "page": page,
                "per_page": per_page,
                "records": records
            }

        finally:
            cursor.close()
            conn.close()

    async def get_audio_blob(self, audio_id: str) -> bytes:
        """
        获取音频 blob 数据

        Args:
            audio_id: 音频记录 ID

        Returns:
            音频二进制数据
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                f"SELECT audio FROM {self.audio_table} WHERE id = %s",
                (audio_id,)
            )
            result = cursor.fetchone()

            if not result or not result[0]:
                raise ValueError(f"音频 {audio_id} 不存在或内容为空")

            logger.info(f"获取音频 blob: {audio_id}, size={len(result[0])} bytes")
            return result[0]

        finally:
            cursor.close()
            conn.close()

    async def get_audio_records_batch(self, audio_ids: list[str]) -> list[dict]:
        """
        批量获取音频记录（含 blob）

        Args:
            audio_ids: 音频 ID 列表

        Returns:
            [{audio_id, title, blob, size, format}, ...]
        """
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            results = []
            for audio_id in audio_ids:
                cursor.execute(
                    f"""
                    SELECT
                        a.id as audio_id,
                        SUBSTRING(h.content, 1, 50) as title,
                        a.audio as blob_data
                    FROM {self.audio_table} a
                    LEFT JOIN {self.history_table} h ON a.id = h.audio_id
                    WHERE a.id = %s
                    LIMIT 1
                    """,
                    (audio_id,)
                )
                row = cursor.fetchone()
                if row and row["blob_data"]:
                    results.append({
                        "audio_id": row["audio_id"],
                        "title": row["title"] or "(无标题)",
                        "blob": row["blob_data"],
                        "size": len(row["blob_data"])
                    })

            logger.info(f"批量获取音频: 请求 {len(audio_ids)}, 获取 {len(results)} 条")
            return results

        finally:
            cursor.close()
            conn.close()
