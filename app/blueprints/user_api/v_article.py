from . import bp_user_api
from ...api_utils import *
from ...models import Article, ArticleType


@bp_user_api.route('/article/list/<int:article_type_id>/', methods=['GET'])
def get_user_article_list(article_type_id):
    """公众号文章列表"""
    article_type = ArticleType.get_by_id(article_type_id, code=1104)
    item = article_type.to_dict()
    query = Article.select().where(Article.article_type_id == article_type_id, Article.is_delete == 0)
    _articles = list()
    for article in query:
        item = article.to_dict()
        item['total_use_count'] = item['real_use_count'] + item['extra_add_count']
        _articles.append(item)
    item['article_list'] = _articles
    data = {
        "articles": _articles
    }
    return api_success_response(data)


@bp_user_api.route('/article/detail/<int:article_id>/', methods=['GET'])
def get_user_article_detail(article_id):
    """公众号单个文章详情"""
    article = Article.get_by_id(article_id, code=1104)
    data = {
        "article": article.to_dict()
    }
    return api_success_response(data)