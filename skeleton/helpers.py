import functools

import simplejson


json_encode = functools.partial(simplejson.dumps, separators=(',', ':'), sort_keys=True)
json_decode = simplejson.loads
