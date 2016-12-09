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
    'name': lambda self, f, *args: 'Author %s' % str(f.id),
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
        'title': lambda self, f, key, *args: '%s %s' % (key, str(f.id))
    }
)

```

## The Breakdown


```python
```
