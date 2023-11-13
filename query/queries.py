from sqlalchemy import text


# db에서 이미지가 없는 URL을 가져옵니다.
def get_data_without_image_url(limit: int, media: str) -> text:
    return text(
        f"""SELECT * FROM portal_news
WHERE image_url = 'no image' AND portal = '{media}'
ORDER BY id DESC
LIMIT {limit};
"""
    )


def get_data_with_date_range(start_date: str, end_date: str, media: str) -> text:
    return text(
        f"""SELECT * FROM portal_news
WHERE image_url = 'no image' AND portal = '{media}'
AND created BETWEEN '{start_date}' AND '{end_date}'
"""
    )


# db에서 이미지url을 업데이트합니다.
def update_image_url(id: int, image_url: str) -> text:
    return text(
        f"""UPDATE portal_news
SET image_url = '{image_url}' AND updated = NOW()
WHERE id = {id};
"""
    )
