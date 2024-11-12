CRLF = "\r\n"

REQUEST_LINE_MATCHER = r"(?P<method>GET|POST) (?P<resource>/[\w./]*)"
PATH_PARAM_MATCHER = r"\{(?P<path_param>\w+)\}"
