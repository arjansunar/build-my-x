import re
from typing import Callable, Literal
from app import request, response


class Router:
    route_map: dict[
        str,
        tuple[Literal["GET", "POST"], Callable[[request.Request], response.Response]],
    ] = {}

    def add_route(
        self,
        path: str,
        method: Literal["GET", "POST"],
        handler: Callable[[request.Request], response.Response],
    ):
        self.route_map[path] = (method, handler)

    def route(self, path: str, method: Literal["GET", "POST"] = "GET"):
        def decorator(func: Callable[[request.Request], response.Response]):
            self.route_map[path] = (method, func)
            return func  # Return the decorated function

        return decorator

    def post(self, path: str):
        def decorator(func: Callable[[request.Request], response.Response]):
            self.route_map[path] = ("POST", func)
            return func  # Return the decorated function

        return decorator

    def get(self, path: str):
        def decorator(func: Callable[[request.Request], response.Response]):
            self.route_map[path] = ("GET", func)
            return func  # Return the decorated function

        return decorator

    def run(self, request: request.Request) -> bytes:
        for path, (method, handler) in self.route_map.items():
            if request.method != method:
                continue
            match = re.search(path, request.resource)
            # pprint({"req": request, "path": path})
            if match:
                # pprint({"matched": match.groupdict(), "path": path})
                request.params = match.groupdict()
                return handler(request).build()
        # none path matched
        return response.response_builder(404, "Not Found").encode()
