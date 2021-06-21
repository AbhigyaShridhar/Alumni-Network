import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

def list_entries(type):
    #To get the titles of all entrie of a given type
    _, filenames = default_storage.listdir(type)
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))

def save_entry(title, content, type):
    filename = f"{type}/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))

def get_entry(title, type):
    try:
        f = default_storage.open(f"{type}/{title}.md")
        #utf-8 is the safest encoding to be used in HTML templates
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None
