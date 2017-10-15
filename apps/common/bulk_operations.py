from collections import OrderedDict
from functools import wraps
from rest_framework import routers, status
from rest_framework.response import Response
from rest_framework.settings import api_settings


def _safe_run(func, *args, **kwargs):
    """
    Try to run a function with given arguments. If it raises an exception, try
    to convert it to response with the exception handler. If that fails, the
    exception is re-raised.
    """
    try:
        return func(*args, **kwargs)
    except Exception as exc:
        response = api_settings.EXCEPTION_HANDLER(exc, context=kwargs)
        if response is not None:
            return response
        raise


def _may_append_response_msg(response, msg_array, identifier):
    msg = None
    for key in ('detail', 'msg', 'non_field_errors'):
        if response.data.get(key):
            msg = response.data.get(key)
            break
    if msg:
        msg_array.append("%s: %s" % (str(identifier), msg))


def _may_add_msg_to_result(msg_array, result):
    msg_result = None
    if msg_array:
        msg_result = msg_array
        if len(msg_array) == 1:
            msg_result = msg_array[0]
    if msg_result:
        result['msg'] = msg_result


def bulk_create_wrapper(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        """
        try to make response looks like:
        {
            "totalCount": 3,
            "createdCount": 2,
            "failed": ["zhangsan"]
        }
        """
        data = request.data
        if not isinstance(data, list):
            return func(self, request, *args, **kwargs)
        total_count = created_count = 0
        failed_objs = []
        msg_array = []
        for idx, obj in enumerate(data):
            request._full_data = obj
            response = _safe_run(func, self, request, *args, **kwargs)
            if status.is_success(response.status_code):
                created_count += 1
            else:
                if isinstance(obj, dict) and len(obj) == 1:
                    failed_objs.append(list(obj.values())[0])
                    _may_append_response_msg(response, msg_array, list(obj.values())[0])
                else:
                    failed_objs.append(obj)
                    _may_append_response_msg(response, msg_array, obj)
            total_count += 1
            # Reset object in view set.
            setattr(self, 'object', None)
        result = {"totalCount": total_count, "createdCount": created_count, "failed": failed_objs}
        _may_add_msg_to_result(msg_array, result)
        return Response(result, status=status.HTTP_200_OK)
    return wrapper


def bulk_destroy_impl(self, request, **kwargs):
    """
    It is possible to delete multiple items in one request. Use the `DELETE`
    method with the same url as for listing/creating objects. The request body
    should contain a list with identifiers for objects to be deleted. The
    identifier is usually the last part of the URL for deleting a single
    object.
    the successful response could be:

    {
            "totalCount": 3             // 成功添加用户成员个数
            "deletedCount": 2           // 删除成功的用户名
            "failed": ["renhaitao"]     // 删除失败的用户名
    }
    """
    if not isinstance(request.data, list):
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={'detail': 'Bulk delete needs a list of identifiers.'})
    for identifier in request.data:
        if not isinstance(identifier, str) and not isinstance(identifier, int):
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'detail': '"%s" is not a valid identifier.' % identifier})
    self.kwargs.update(kwargs)
    total_count = deleted_count = 0
    failed_ids = []
    msg_array = []
    for identifier in OrderedDict.fromkeys(request.data):
        self.kwargs[self.lookup_field] = str(identifier)
        response = _safe_run(self.destroy, request, **self.kwargs)
        if status.is_success(response.status_code):
            deleted_count += 1
        else:
            failed_ids.append(identifier)
            _may_append_response_msg(response, msg_array, identifier)
        total_count += 1

    result = {"totalCount": total_count, "deletedCount": deleted_count, "failed": failed_ids}
    _may_add_msg_to_result(msg_array, result)
    # it actually return content, so should not  return 204
    # no content.
    return Response(result, status=status.HTTP_200_OK)


class BulkRouter(routers.DefaultRouter):
    """
    This router provides the standard set of resources (the same as
    `DefaultRouter`). In addition to that, it allows for bulk operations on the
    collection as a whole. These are performed as a POST/DELETE request on
    the `{basename}-list` url. These requests are dispatched to the
    `bulk_create` and `bulk_destroy` methods
    respectively.
    """
    def get_routes(self, viewset):
        for route in self.routes:
            if isinstance(route, routers.Route) and route.name.endswith('-list'):
                route.mapping.update({'delete': 'bulk_destroy'})
        return super().get_routes(viewset)

    def register(self, prefix, viewset, base_name=None):
        if hasattr(viewset, 'create'):
            viewset.create = bulk_create_wrapper(viewset.create)
        if hasattr(viewset, 'destroy') and not hasattr(viewset, 'bulk_destroy'):
            viewset.bulk_destroy = bulk_destroy_impl
        super().register(prefix, viewset, base_name)
