from . import bp_user_api
from ...api_utils import *
from ...models import Article


@bp_user_api.route('/article/list/', methods=['GET'])
def get_user_article_list():
    """公众号文章列表"""
    query = Article.select().where(Article.is_delete == 0, Article.show == 1).order_by(Article.weight.desc())
    _article = list()
    for article in query:
        item = article.to_dict()
        item['total_use_count'] = item['real_use_count'] + item['extra_add_count']
        _article.append(item)
    data = {
        "articles": _article
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