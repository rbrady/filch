# The MIT License (MIT)
#
# Copyright (c) 2018 Ryan Brady <ryan@ryanbrady.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import os
from pprint import pprint

import jinja2

from filch import boards
from filch import configuration


class ContextMixin:
    """
    A default context mixin that passes the keyword arguments received by
    get_context_data() as the template context.
    """
    extra_context = None

    def get_context_data(self, **kwargs):
        kwargs.setdefault('view', self)
        if self.extra_context is not None:
            kwargs.update(self.extra_context)
        return kwargs


class TemplateRenderMixin:
    template_name = None

    def get_template_names(self):
        """
        Return a list of template names to be used for the report. Must return
        a list. May not be called if render_to_report() is overridden.
        """
        if self.template_name is None:
            raise ImproperlyConfigured(
                "TemplateRenderMixin requires either a definition of "
                "'template_name' or an implementation of 'get_template_names()'")
        else:
            return [self.template_name]

    def render_to_report(self, context):
        # if there is a template present for the output, then merge the template
        # with the data
        with open(self.get_template_names(), 'r') as template_file:
            template_data = template_file.read()
            # Render the j2 template
            raw_template = jinja2.Environment().from_string(
                template_data)
            return raw_template.render(**context)


class FileWriterMixin:
    output_name = None

    def get_output_names(self):
        """
        Return a list of template names to be used for the report. Must return
        a list. May not be called if write_to_file() is overridden.
        """
        if self.output_name is None:
            raise ImproperlyConfigured(
                "TemplateRenderMixin requires either a definition of "
                "'output_name' or an implementation of 'get_output_names()'")
        else:
            return [self.output_name]

    def write_to_file(self, content):
        # if there is an output arg, write to a file of that name.
        with open(self.output_name, 'w') as output_file:
            output_file.write(content)


class Report:

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def as_report(cls, **initkwargs):
        for key in initkwargs:
            if not hasattr(cls, key):
                raise TypeError(
                    "%s() received an invalid keyword %r. as_report only "
                    "accepts arguments that are already attributes of the "
                    "class." % (cls.__name__, key))


class FileReport(TemplateRenderMixin, FileWriterMixin, ContextMixin, Report):

    def get(self, **kwargs):
        context = self.get_context_data(**kwargs)
        output = self.render_to_response(context)
        self.write_to_file(output)
