# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------
"""Common functions shared by both the sync and the async decorators."""
from contextlib import contextmanager

from azure.core.tracing.abstract_span import AbstractSpan
from azure.core.settings import settings


try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, Optional, Union, Callable, List, Type, Generator


def get_function_and_class_name(func, *args):
    # type: (Callable, List[Any]) -> str
    """
    Given a function and its unamed arguments, returns class_name.function_name. It assumes the first argument
    is `self`. If there are no arguments then it only returns the function name.

    :param func: the function passed in
    :type func: `collections.abc.Callable`
    :param args: List of arguments passed into the function
    :type args: List[Any]
    """
    try:
        return func.__qualname__
    except AttributeError:
        if args:
            return "{}.{}".format(args[0].__class__.__name__, func.__name__)  # pylint: disable=protected-access
        return func.__name__

@contextmanager
def change_context(span):
    # type: (Optional[AbstractSpan]) -> Generator
    """Execute this block inside the given context and restore it afterwards.

    This does not start and ends the span, but just make sure all code is executed within
    that span.

    If span is None, no-op.

    :param span: A span
    :type span: AbstractSpan
    """
    span_impl_type = settings.tracing_implementation()  # type: Type[AbstractSpan]
    if span_impl_type is None or span is None:
        yield
    else:
        original_span = span_impl_type.get_current_span()
        try:
            span_impl_type.set_current_span(span)
            yield
        finally:
            span_impl_type.set_current_span(original_span)


def with_current_context(func):
    # type: (Callable) -> Any
    """Passes the current spans to the new context the function will be run in.

    :param func: The function that will be run in the new context
    :return: The target the pass in instead of the function
    """
    span_impl_type = settings.tracing_implementation()  # type: Type[AbstractSpan]
    if span_impl_type is None:
        return func

    return span_impl_type.with_current_context(func)
