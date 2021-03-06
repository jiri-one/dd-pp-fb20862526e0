import falcon
from uuid import uuid4
from os import mkdir
# internal imports
from helpers import render_template
from db import cwd, check_password, db_users, query, register_user, db_init


class Authorize(object):
    """@falcon.before decorator for authorize if successful login - works on GET and POST methodes"""

    def __call__(self, req, resp, resource, params):
        resp.context.authorized = 0
        if req.get_cookie_values('cookie_uuid') and req.get_cookie_values('user'):
            cookie_uuid = req.get_cookie_values('cookie_uuid')[0]
            user = req.get_cookie_values('user')[0]
            cookie_from_db = db_users.search(query.name == user)[0]["cookie_uuid"]
            if cookie_uuid == cookie_from_db:
                resp.context.authorized = 1
                resource.user = user
                resource.db = db_init(user)
            else:
                resp.unset_cookie('cookie_uuid')  # only for sure
                resp.unset_cookie('user')
                if req.relative_uri != "/login":
                    raise falcon.HTTPSeeOther("/login")
        else:
            resp.unset_cookie('cookie_uuid')  # only for sure
            resp.unset_cookie('user')
            if req.relative_uri != "/login":
                raise falcon.HTTPSeeOther("/login")

class LoginResource(object):
    @falcon.before(Authorize())
    @falcon.after(render_template, "login.mako")
    def on_get(self, req, resp):
        if resp.context.authorized == 1:
            raise falcon.HTTPSeeOther("/")
        else:
            resp.text = {}
    
    def on_post(self, req, resp):
        form_data = {}
        for part in req.media:
            form_data[part.name] = part.data.decode()

        login = form_data["login"]
        passwd = form_data["password"]
        try:
            if check_password(passwd, db_users.search(query.name == login)[0]["password"]):
                new_cookie = str(uuid4())
                db_users.update({'cookie_uuid': new_cookie}, query.name == login)
                resp.set_cookie('cookie_uuid', new_cookie,
                                max_age=72000, secure=True)
                resp.set_cookie('user', login,
                                max_age=72000, secure=True)
                raise falcon.HTTPSeeOther("/")
            else:
                raise falcon.HTTPUnauthorized("Bad login or password! (??patn?? jm??no nebo heslo!)")
        except IndexError as e:
            raise falcon.HTTPUnauthorized("Va??e jm??no nebo heslo z??ejm?? nen?? v??bec v datab??zi, registrujte se pros??m.")
    
    def on_get_logout(self, req, resp):
        resp.unset_cookie('cookie_uuid')
        resp.unset_cookie('user')
        raise falcon.HTTPSeeOther("/login")


    @falcon.after(render_template, "register.mako")
    def on_get_register(self, req, resp):
        if req.get_cookie_values('cookie_uuid') and req.get_cookie_values('user'):
            resp.text = {"error": """P??ihl????en?? u??ivatel?? nemohou prov??d??t registrace! Mus??te se nejd????ve <a href="/logout">odhl??sit.</a>"""}
        else:
            resp.text = {}
    
    @falcon.after(render_template, "register.mako")
    def on_post_register(self, req, resp):
        form_data = {}
        for part in req.media:
            form_data[part.name] = part.data.decode()
        login = form_data["login"]
        passwd = form_data["password"]
        try:
            new_user_id = register_user(login, passwd)
            mkdir(cwd / f"files/{login}")
        except ValueError as e:
            resp.text = {"error": e}
        except FileExistsError as e:
            resp.text = {"error": "Adres???? s t??mto u??ivatelsk??m jm??nem u?? existuje, zvolte si jin??."}
        else:
            raise falcon.HTTPStatus('202 Accepted', text=f'Registrace prob??hla ??sp????n??. Byl registrov??n u??ivatel s ID {new_user_id} a u??ivatelsk??m jm??nem {login}. Pokra??ujte na <a href="/login">p??ihla??ovac?? str??nku</a>.')




    

    
