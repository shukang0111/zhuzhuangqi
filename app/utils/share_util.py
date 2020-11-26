from app.models import Article, Video


def update_share_times(cid, tid):
    """更新分享次数"""
    item = dict()
    if tid == 1:  # 海报
        pass
    elif tid == 2:  # 文章
        article = Article.get_by_id(cid)
        article.update_real_use_count()
        item = article.to_dict()
    elif tid == 4:  # 视频
        video = Video.get_by_id(cid)
        video.update_real_use_count()
        item = video.to_dict()
    return item
