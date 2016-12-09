[![Build Status](https://travis-ci.org/Rhathe/fixtureupper.svg?branch=master)](https://travis-ci.org/Rhathe/fixtureupper)

# fixtureupper
A library to generate and save/load SqlAlchemy fixtures


# Examples

## The Fixup

```python
from fixtureupper.register import UpperRegister
from fixtureupper.defaults import inherit
from yourapp.models import Author, Article


# First create register class for your fixtureuppers
FixtureUpperRegister = UpperRegister('SqlAlchemyModel')


# Register model fixture uppers to register class by subclassing

class AuthorFixtureUpper(FixtureUpperRegister):
    model = Author


class ArticleFixtureUpper(FixtureUpperRegister):
    model = Article


# Create base fixture upper instance
new_fixtureupper = FixtureUpperRegister()

# Get author fixtureupper instance, using model's class name
au_fu = new_fixtureupper.get_upper('Author')

# Generate Author with id=1
author_1 = au_fu.fixup()

# Generate Author with id=2, name='Test Author'
author_2 = au_fu.fixup({'name': 'Test Author'})

# Get article fixtureupper instance, set start_id as 100
ar_fu = new_fixtureupper.get_upper('Article', start_id=100)

# Generate Article with id=100, author=author_2, main_author_id=2
article_1 = ar_fu.fixup({'author': author_2})

# Generate array of 2 Articles with id=999 and id=101
article_2, article_3 = ar_fu.fixup([{'id': 999}, {}])

# Generate author with id=3, articles=[article_2]
# Sets article_2's main_author_id to 3
author_3 = au_fu.fixup({'article': article_2})

# Generate author with id=99, name='Author 99'
author_4 = au_fu.fixup({
    'id': 99,
    'name': lambda self, current_fixture, *args: 'Author %s' % str(current_fixture.id),
})

# Generate Article with id=102, author=author_4, main_author_id=4, title='Author 99'
article_4 = ar_fu.fixup({
    'author': author_4,
    'title': inherit('author', 'name'),
})

# Generate array of 2 Articles with id=1999, title='title 1999' and id=2999, title='title 2999'
article_5, article_6 = ar_fu.fixup(
    [{'id': 1999}, {'id': 2999}],
    defaults={
        'title': lambda self, current_fixture, key, *args: '%s %s' % (key, str(current_fixture.id))
    }
)

# Get array of Article and Author with both ids=3000, title and name='JSON 3000' from json string
article_7, author_5 = new_fixtureupper.fixup_from_json("""
[
    {
        "__class__": "Article",
        "__value__": {
            "id": 3000,
            "title": "JSON 3000"
        }
    },
    {
        "__class__": "Author",
        "__value__": {
            "id": 3000,
            "name": "JSON 3000"
        }
    }
]
""")


# Get fixtures from file
file_fixtures = new_fixtureupper.read_json_breakdown('path/to/breakdown.json')
```

## The Breakdown


```python
# Fixup fixtures
new_fixtureupper = FixtureUpperRegister()
new_fixtureupper.get_upper('Article').fixup()
new_fixtureupper.get_upper('Author').fixup([{'id': 10, 'name': 'Author Name'}, {}])

# Breakdown to json string:
# [
#     {
#         "__class__": "Article",
#         "__value__": {
#             "id": 1
#         }
#     },
#     {
#         "__class__": "Author",
#         "__value__": {
#             "id": 10,
#             "name": "Author Name"
#         }
#     },
#     {
#         "__class__": "Author",
#         "__value__": {
#             "id": 1
#         }
#     }
# ]
json_breakdown = new_fixtureupper.get_current_json_breakdown()

# Print json breakdown to path/to/new_breakdown.json
new_fixtureupper.print_json_breakdown('path/to', 'new_breakdown.json', json_breakdown)

# Breakdown to sql string:
# INSERT INTO article (id) VALUES
# (1);
#
# INSERT INTO author (id, name) VALUES
# (10, 'Author Name'),
# (1, NULL);
sql_breakdown = new_fixtureupper.get_current_sql_breakdown()

# Print sql breakdown to path/to/new_breakdown.sql
new_fixtureupper.print_sql_breakdown('path/to', 'new_breakdown.sql', sql_breakdown)
```
