[![Build Status](https://travis-ci.org/Rhathe/fixtureupper.svg?branch=master)](https://travis-ci.org/Rhathe/fixtureupper)

# fixtureupper
A library to generate and save/load SqlAlchemy fixtures


# Examples

## The Fixup

Generate fixtures using the fixtureupper fixup method

### Basic Usage

```python
from fixtureupper.register import UpperRegister
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

# Get array of author fixtures: i.e [author_1, author_2, author_3]
current_author_fixtures = au_fu.fixtures

# Get array of all fixtures: i.e [article_1, article_2, article_3, author_1, author_2, author_3]
all_current_fixtures = new_fixture_upper.get_all_fixtures()
```

You can pass generator functions to the data, and refer to the current fixture as it builds.
Functions generate values after static values are set first, so you can refer to a fixture's
static value in your generator functions.

```python
from fixtureupper.defaults import inherit

# Generate author with id=99, name='Author 99'
author = au_fu.fixup({
    'id': 99,
    'name': lambda self, current_fixture, *args: 'Author %s' % str(current_fixture.id),
})

# inherit is a helper function that takes a value from a relation
# In this example, the title of the article is the same as the author's name
# If author had a title attribute, you don't have to pass a second arg into inherit
# Generate Article with id=100, author=author, main_author_id=99, title='Author 99'
article = ar_fu.fixup({
    'id': 100,
    'author': author,
    'title': inherit('author', 'name'),
})
```

If all the fixtures you want to fixup share common static values/generators,
you can pass them into the kwarg `defaults`, or set the defaults attribute
when declaring the fixtureupper class for your model

NOTE: passing in a kwarg `defaults` will cause the fixtureupper to ignore it's class attribute `defaults`.
If you want to override certain class defaults but keep the others use the kwarg `default_overrides` instead

```python
# Generate array of 2 Articles with id=1999, title='title 1999' and id=2999, title='title 2999'
article_1999, article_2999 = ar_fu.fixup(
    [{'id': 1999}, {'id': 2999}],
    defaults={
        'title': lambda self, current_fixture, key, *args: '%s %s' % (key, str(current_fixture.id)),
    }
)
```

You can load fixtures from a json instead of generating them at runtime.
Useful for getting fixtures from a file that was already previously generated.

```python
# Get array of Article and Author with both ids=3000, title and name='JSON 3000' from json string
article, author = new_fixtureupper.fixup_from_json("""
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

### Constructing fixtureupper classes

```python
from yourapp.models import Draft

FixtureUpperRegister = UpperRegister('SqlAlchemyModel')


class ArticleFixtureUpper(FixtureUpperRegister):
    model = Article

    # sub_title is a generator function that relies on the fixture's title being set first
    # but the title is also a generator function and thus order is ambiguous
    # Therefore, set an order where sub_title comes after title
    generated_field_order = ['title', 'sub_title']

    defaults = {
        # refer to a ArticleFixtureUpper method
        'title': lambda self, *args: self.get_title(*args),

        'sub_title': lambda self, fixture, *args: 'sub title for "%s"' % fixture.title,

        # Use self.random, as that is seeded by a default
        # And thus creates the same values if generated multiple times
        # seed can be overwritten when first calling get_upper, .i.e:
        # new_fixtureupper.get_upper('Article', seed='new_seed')
        'is_visible': lambda self, *args: bool(self.random.getrandbits(1)),
    }

    get_title(self, fixture, attribute_name, *args):
        return 'default article %s for %s' % (attribute_name, fixture.id)


class DraftFixtureUpper(FixtureUpperRegister):
    model = Draft

    defaults = {
        # inherit article's title
        'title': inherit('article'),

        'sub_title': 'default draft sub title',

        # Create a new article if no article passed in
        # Relation attributes are by default generated before other attributes
        # so no need to specify generated_field_order
        # Would have to if article depended on title for example though
        'article': lambda self, *args: self.get_upper('Article').fixup(),
    }

new_fixtureupper = FixtureUpperRegister(start_id=10)
dr_fu = new_fixtureupper.get_upper('Draft', start_id=20)

# Generate draft with id=20, sub_title='default draft sub title'
# article=(article with id=10, title='default article title for 10',
#          sub_title='sub title for "default title for 10"',
#          and random is_visible),
# and title='default article title for 10'
draft_1 = dr_fu.fixup()

# Generate draft with id=21, sub_title='default draft sub title'
# article=draft_1.article, and title='new draft title'
draft_2 = dr_fu.fixup({
    'article': draft1.article,
    'title': lambda self, fixture, key, *args: 'new draft %s' % key,
})

# Generate drafts with id=22, and id=23
draft_3, draft_4 = dr_fu.fixup([{}, {}], defaults={})

# Generate drafts with sub_title='default draft sub title'
# article=draft_1.article, title=None,
# and ids=(24 and 25)
draft_4, draft_5 = dr_fu.fixup([{}, {}], default_overrides={
    'article': draft_1.article,
    'title': None,
})
```

## The Breakdown

Breakdown fixtures into string representations, to either save as a static json representation
so you can now exactly what values are loaded into your fixtures,
or as a sql command to execute directly into a database

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
