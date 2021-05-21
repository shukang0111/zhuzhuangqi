from flask import g, request

from . import bp_admin_api
from ...api_utils import *
from ...models import Article, ArticleType


@bp_admin_api.route('/article_type/create/', methods=['POST'])
def create_article_type():
    """创建文章分类"""
    name = request.json.get("name")
    claim_args_str(1204, name)
    ArticleType.new(name)
    return api_success_response({})


@bp_admin_api.route('/article_type/edit/', methods=['POST'])
def edit_article_type_name():
    """编辑文章分类名称"""
    article_type_id, name = map(g.json.get, ['article_type_id', 'name'])
    claim_args(1203, article_type_id, name)
    claim_args_int(1204, article_type_id)
    claim_args_str(1204, name)
    article_type = ArticleType.get_by_id(article_type_id, code=1104)
    article_type.name = name
    article_type.save()
    return api_success_response({})


@bp_admin_api.route('/article_type/delete/', methods=['POST'])
def delete_article_type():
    """删除文章分类"""
    article_type_id = g.json.get("article_type_id")
    claim_args_int(1204, article_type_id)
    article_type = ArticleType.get_by_id(article_type_id, code=1104)
    # query = Article.select().where(Article.article_type_id == article_type_id, Article.is_delete == 0)
    # for article in query:
    #     article.update_delete(is_delete=1)
    article_type.update_delete(is_delete=1)
    return api_success_response({})


@bp_admin_api.route('/article_type/all/', methods=['GET'])
def get_all_article_type():
    """查询所有文章分类"""
    query = ArticleType.select().where(ArticleType.is_delete == 0).order_by(ArticleType.weight.asc())
    data = {
        "article_types": [article_type.to_dict() for article_type in query]
    }
    return api_success_response(data)


@bp_admin_api.route('/article_type/sort/', methods=['POST'])
def article_type_sort():
    """
    文章分类排序
    :return:
    """
    article_types = g.json.get("article_types")
    article_type_ids = [item.get('id') for item in article_types]
    query = ArticleType.select().where(ArticleType.id.in_(article_type_ids))
    type_id_entity_map = {item.id: item for item in query}
    for item in article_types:
        weight = item.get('weight', 0)
        article_type = type_id_entity_map.get(item.get('id', 0))
        if article_type is None:
            continue
        article_type.weight = weight
        article_type.save()
    return api_success_response({})


@bp_admin_api.route('/article/create/', methods=['POST'])
def create_article():
    """创建文章"""
    article_type_id, title, contents, cover_url, extra_add_count, description = map(g.json.get, ['article_type_id', 'title', 'contents', 'cover_url', 'extra_add_count', 'description'])
    claim_args(1203, title, contents, cover_url)
    claim_args_int(1204, extra_add_count)
    claim_args_str(1204, title, contents, cover_url)
    article = Article.new(article_type_id, title, contents, cover_url, extra_add_count)
    if description:
        article.description = description
        article.save()
    return api_success_response({})


@bp_admin_api.route('/article/status/update/', methods=['POST'])
def update_article_status():
    """启用/停用文章"""
    article_id, show = map(g.json.get, ['article_id', 'show'])
    claim_args(1203, article_id, show)
    claim_args_int(1204, article_id, show)
    article = Article.get_by_id(article_id, code=1104)
    article.update_show(show)
    return api_success_response({})


@bp_admin_api.route('/article/delete/', methods=['POST'])
def delete_article():
    """删除文章"""
    article_id = g.json.get('article_id')
    claim_args_int(1204, article_id)
    article = Article.get_by_id(article_id, code=1104)
    # article.update_delete(is_delete=1)
    article.delete_instance()
    return api_success_response({})


@bp_admin_api.route('/article/edit/', methods=['POST'])
def edit_article():
    """编辑文章"""
    article_id, title, contents, cover_url, extra_add_count = map(g.json.get, ['article_id', 'title', 'contents', 'cover_url', 'extra_add_count'])
    claim_args(1203, article_id, title, contents, cover_url)
    claim_args_int(1204, article_id, extra_add_count)
    claim_args_str(1204, title, contents, cover_url)
    article = Article.get_by_id(article_id, code=1104)
    article.update_info(title, contents, cover_url, extra_add_count)
    return api_success_response({})


@bp_admin_api.route('/article/list/<int:article_type_id>/', methods=['GET'])
def get_article_list(article_type_id):
    """查询文章list"""
    article_type = ArticleType.get_by_id(article_type_id, code=1104)
    item = article_type.to_dict()
    query = Article.select().where(Article.article_type_id == article_type_id, Article.is_delete == 0)
    _articles = list()
    for article in query:
        _articles.append(article.to_dict())
    item['article_list'] = _articles
    data = {
        "articles": item
    }
    return api_success_response(data)


@bp_admin_api.route('/article/detail/<int:article_id>/', methods=['GET'])
def get_article_detail(article_id):
    """查询单个文章详情"""
    article = Article.get_by_id(int(article_id), code=1104)
    item = article.to_dict()
    item['description'] = '' if not article.description else article.description
    data = {
        "article": article.to_dict()
    }
    return api_success_response(data)


@bp_admin_api.route('/articles/', methods=['POST'])
def get_articles():
    """
    导入文章查询页
    :return:
    """
    article_type_id = g.json.get('article_type_id', '0')
    # article_ids = g.json.get('article_ids', [])
    search_key = g.json.get('search_key', '')
    article_type = ArticleType.get_by_id(article_type_id, code=1104)
    item = article_type.to_dict()
    if len(search_key) > 0:
        query = Article.select().where(Article.title.contains(search_key), Article.is_delete == 0)
    if article_type_id != 0:
        query = Article.select().where(Article.article_type_id == article_type_id, Article.is_delete == 0)
    _articles = list()
    for article in query:
        item = {
            'id': article.id,
            'title': article.title
        }
        _articles.append(item)
    data = {
        "articles": _articles
    }
    return api_success_response(data)


@bp_admin_api.route('/article/import/', methods=['POST'])
def import_articles():
    """
    系统后台导入文章

    :return:
    """
    article_type_id = g.json.get('article_type_id', 0)
    article_ids = g.json.get('article_ids', [])
    articles = Article.select().where(Article.id.in_(article_ids))
    article_list = []
    for item in articles:
        article = Article()
        article.article_type_id = article_type_id
        article.title = item.title
        article.contents = item.contents
        article.cover_url = item.cover_url
        article.extra_add_count = item.extra_add_count
        article.description = item.description
        article.show = item.show
        article_list.append(article)
    Article.bulk_create(article_list)

    return api_success_response({})

