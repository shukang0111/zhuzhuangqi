from . import bp_user_api
from ...api_utils import *
from ...models import Article, ArticleType


@bp_user_api.route('/article_type/all/', methods=['GET'])
def get_all_article_type():
    """查询所有文章分类"""
    query = ArticleType.select().where(ArticleType.is_delete == 0, ArticleType.show == 1)
    data = {
        "article_types": [article_type.to_dict() for article_type in query]
    }
    return api_success_response(data)


@bp_user_api.route('/article/list/<int:article_type_id>/', methods=['GET'])
def get_user_article_list(article_type_id):
    """公众号文章列表"""
    article_type = ArticleType.get_by_id(article_type_id, code=1104)
    item = article_type.to_dict()
    query = Article.select().where(Article.article_type_id == article_type_id, Article.is_delete == 0)
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
