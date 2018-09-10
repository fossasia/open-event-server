"""
HTTP filter helpers

As defined by the jsonapi http://jsonapi.org/format/#fetching-filtering, the
filter can contain anything. For this project, the format is predefined by the
flask json rest api library and is a json string with the following format:

```json
filter: [
   {
     name : 'event',
     op   : 'operand',
     val  : 'value for operand'
   }
 ]
```
"""

import json
from collections import namedtuple


def json_to_rest_filter_list(json_string):
    """
    Converts a json string to a rest filter object list
    """
    json_dict_list = json.loads(json_string)

    return [
        namedtuple('RestFilter', sorted(json_dict))(**json_dict)
        for json_dict in json_dict_list
    ]
