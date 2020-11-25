from flask import g, request

from . import bp_admin_api
from ...api_utils import *
from ...models import Article, ArticleType


@bp_admin_api.route('/article_type/create/', methods=['POST'])
def create_article_type():
    """创建文章分类"""
    name = request.json.get("name")
    claim_args_str(1204, name)
    article_type = ArticleType.get_by_name(name)
    claim_args_true(1304, not article_type)
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
    query = Article.select().where(Article.article_type_id == article_type_id)
    for article in query:
        article.update_delete(is_delete=1)
    article_type.update_delete(is_delete=1)
    return api_success_response({})


@bp_admin_api.route('/article_type/all/', methods=['GET'])
def get_all_article_type():
    """查询所有文章分类"""
    query = ArticleType.select().where(ArticleType.is_delete == 0)
    data = {
        "article_types": [article_type.to_dict() for article_type in query]
    }
    return api_success_response(data)


@bp_admin_api.route('/article/create/', methods=['POST'])
def create_article():
    """创建文章"""
    article_type_id, title, contents, cover_url, extra_add_count = map(g.json.get, ['article_type_id', 'title', 'contents', 'cover_url', 'extra_add_count'])
    claim_args(1203, title, contents, cover_url, extra_add_count)
    claim_args_int(1204, extra_add_count)
    claim_args_str(1204, title, contents, cover_url)
    Article.new(title, contents, cover_url, extra_add_count)
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
    article.update_delete(is_delete=1)
    return api_success_response({})


@bp_admin_api.route('/article/edit/', methods=['POST'])
def edit_article():
    """编辑文章"""
    article_id, title, contents, cover_url, extra_add_count = map(g.json.get, ['article_id', 'title', 'contents', 'cover_url', 'extra_add_count'])
    claim_args(1203, article_id, title, contents, cover_url, extra_add_count)
    claim_args_int(1204, article_id, extra_add_count)
    claim_args_str(1204, title, contents, cover_url)
    article = Article.get_by_id(article_id, code=1104)
    article.update_info(title, contents, cover_url, extra_add_count)
    return api_success_response({})


@bp_admin_api.route('/article/list/', methods=['GET'])
def get_article_list():
    """查询文章list"""
    query = Article.select().where(Article.is_delete == 0)
    data = {
        "articles": [article.to_dict() for article in query]
    }
    return api_success_response(data)


@bp_admin_api.route('/article/detail/<int:article_id>/', methods=['GET'])
def get_article_detail(article_id):
    """查询单个文章详情"""
    article = Article.get_by_id(int(article_id), code=1104)
    data = {
        "article": article.to_dict()
    }
    return api_success_response(data)

