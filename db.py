from tinydb import TinyDB, Query, JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import bcrypt
import re
# internal imports
from path_serializer import PathSerializer

# set current working directory
cwd = Path(__file__).parent

# set DB files and queries
serialization = SerializationMiddleware(JSONStorage)
serialization.register_serializer(DateTimeSerializer(), 'TinyDate')
serialization.register_serializer(PathSerializer(), 'TinyPath')
db_users = TinyDB(cwd / 'files/db_users.json')
query = Query()


def db_init(user):
    """Importat function for initiating db for every user."""
    return TinyDB(cwd / f'files/{user}/db.json', storage=serialization)

@dataclass
class Task:
    title: str
    content: str
    time_expired: datetime
    time_created: datetime = datetime.now()
    time_finished: datetime = None
    attach: Path = None
    id: int = None
    db: TinyDB = None

    def write_to_db(self):
        self.id = self.db.insert({ 
                    'title': self.title,
                    'content': self.content,
                    'time_expired': self.time_expired,
                    'time_created': self.time_created,
                    'time_finished': self.time_finished,
                    'attach': self.attach,
                    })
    
    def update_in_db(self):
        self.db.update({ 
                    'title': self.title,
                    'content': self.content,
                    'time_expired': self.time_expired,
                    'time_created': self.time_created,
                    'time_finished': self.time_finished,
                    'attach': self.attach,
                    }, doc_ids=[self.id])


def create_task_class(el):
    return Task(title=el["title"],
                content=el["content"],
                time_expired=el["time_expired"],
                time_created=el["time_created"],
                time_finished=el["time_finished"],
                attach=el["attach"],
                id=el.doc_id
                )

def get_task_from_db(db, doc_id):
    el = db.get(doc_id=doc_id)
    if el:
        task = create_task_class(el)
        task.db = db
        return task

def remove_task_from_db(db, doc_id):
    db.remove(doc_ids=[doc_id])


def get_tasks(db, tasks):
    if tasks == "expired":
        result = db.search( (query.time_expired < datetime.now()) &
                            (query.time_finished == None))
    elif tasks == "finished":
        result = db.search(query.time_finished != None)
    else:
        result = db.search( (query.time_expired > datetime.now()) &
                            (query.time_finished == None))
    for el in sorted(result, key=lambda k: k['time_created'], reverse=True):
        yield create_task_class(el)


def search_tasks(db, tasks, searched_word):
    searched_word = searched_word.lower()
    for task in get_tasks(db, tasks):
        if (searched_word in task.title.lower() 
            or searched_word in task.content.lower()):
            yield task

# user, pasword and hash helpers
def get_hashed_password(plain_text_password):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())


def check_password(plain_text_password, hashed_password):
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(plain_text_password, hashed_password)


def register_user(user, passwd):
    if len(db_users.search(query.name == user)) != 0: # username is taken
        raise ValueError("Username is taken! Choose another.")
    new_user_id = db_users.insert({'name': user, 'password': get_hashed_password(passwd)})
    if new_user_id:
        return new_user_id
    else:
        raise ValueError("Database error! Contact administrator.")


# some commands for test
# db_users.insert({'name': 'USER_NAME', 'password': get_hashed_password("XXXXX")})
# print(db_users.search(query.name == 'deso')[0]["password"])
# print(check_password("heslo", db_users.search(query.name == 'deso')[0]["password"]))
