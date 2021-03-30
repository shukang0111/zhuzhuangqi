from flask import g, current_app, request

from . import bp_user_api
from ...api_utils import *
from ...models import Article, ArticleType, Video


@bp_user_api.route('/search/', methods=['GET'])
def search_article_video():
    """
    公众号首页搜索文章&视频
    :return:
    """
    content_type = request.args.get('content_type', 1)  # 1-文章 2-视频
    search_key = request.args.get('search_key', '')
    current_app.logger.info("search_key: {}".format(search_key))
    if len(search_key) < 1:
        return api_success_response({})
    content_list = []
    if content_type == "1":
        query_set = Article.select().where(Article.title.contains(search_key), Article.is_delete == 0, Article.show == 1)
        for item in query_set:
            content_list.append({
                'id': item.id,
                'url': item.cover_url,
                'title': item.title,
                'read_count': item.real_use_count + item.extra_add_count,
                'content_type': 1
            })
    else:
        query_set = Video.select().where(Video.video_title.contains(search_key), Video.is_delete == 0, Video.show == 1)
        for item in query_set:
            content_list.append({
                'id': item.id,
                'url': item.cover_url,
                'title': item.video_title,
                'read_count': item.real_use_count + item.extra_add_count,
                'content_type': 2
            })
    data = {
        'content_list': content_list
    }
    return api_success_response(data)


@bp_user_api.route('/article_type/all/', methods=['GET'])
def get_all_article_type():
    """查询所有文章分类"""
    # 用户选择的分类
    user = g.wx_user
    selected_article_type_ids = list()
    for article_type in user.article_types:
        selected_article_type_ids.append(article_type.id)
    current_app.logger.info(selected_article_type_ids)
    info = list()
    # 所有分类
    query = ArticleType.select().where(ArticleType.is_delete == 0, ArticleType.show == 1)
    for _article_type in query:
        item = _article_type.to_dict()
        if item['id'] in selected_article_type_ids:
            item['is_selected'] = 1
        else:
            item['is_selected'] = 0
        info.append(item)

    data = {
        "article_types": info
    }
    return api_success_response(data)


@bp_user_api.route('/article/list/<int:article_type_id>/', methods=['GET'])
def get_user_article_list(article_type_id):
    """公众号文章列表"""
    article_type = ArticleType.get_by_id(article_type_id, code=1104)
    item = article_type.to_dict()
    query = Article.select().where(Article.article_type_id == article_type_id, Article.is_delete == 0, Article.show == 1)
    _articles = list()
    for article in query:
        _article = article.to_dict()
        _article['total_use_count'] = _article['real_use_count'] + _article['extra_add_count']
        _articles.append(_article)
    item['article_list'] = _articles
    data = {
        "articles": item
    }
    return api_success_response(data)


@bp_user_api.route('/article/detail/<int:article_id>/', methods=['GET'])
def get_user_article_detail(article_id):
    """公众号单个文章详情"""
    article = Article.get_by_id(article_id, code=1104)
    item = article.to_dict()
    item['tid'] = 2
    item['cid'] = article.id
    data = {
        "article": item
    }
    return api_success_response(data)
