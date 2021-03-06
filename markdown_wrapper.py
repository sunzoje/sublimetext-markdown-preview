from __future__ import absolute_import
import sublime

ST3 = int(sublime.version()) >= 3000

if ST3:
    from .markdown import Markdown
    import importlib
else:
    from markdown import Markdown


class StMarkdown(Markdown):
    def __init__(self, *args, **kwargs):
        super(StMarkdown, self).__init__(*args, **kwargs)

    def build_extension(self, ext_name, configs=[]):
        """Build extension by name, then return the module.

        The extension name may contain arguments as part of the string in the
        following format: "extname(key1=value1,key2=value2)"

        """

        # Parse extensions config params (ignore the order)
        configs = dict(configs)
        pos = ext_name.find("(")  # find the first "("
        if pos > 0:
            ext_args = ext_name[pos + 1:-1]
            ext_name = ext_name[:pos]
            pairs = [x.split("=") for x in ext_args.split(",")]
            configs.update([(x.strip(), y.strip()) for (x, y) in pairs])

        # Setup the module name
        module_name = ext_name
        if '.' not in ext_name:
            if ST3:
                from .helper import INSTALLED_DIRECTORY
                module_name = '.'.join([INSTALLED_DIRECTORY, 'markdown.extensions', ext_name])
            else:
                module_name = '.'.join(['markdown.extensions', ext_name])

        # Try loading the extension first from one place, then another
        try:  # New style (markdown.extensons.<extension>)
            if ST3:
                module = importlib.import_module(module_name)
            else:
                module = __import__(module_name, {}, {}, [module_name.rpartition('.')[0]])
        except ImportError:
            module_name_old_style = '_'.join(['mdx', ext_name])
            try:  # Old style (mdx_<extension>)
                module = __import__(module_name_old_style)
            except ImportError as e:
                message = "Failed loading extension '%s' from '%s' or '%s'" \
                    % (ext_name, module_name, module_name_old_style)
                e.args = (message,) + e.args[1:]
                raise

        # If the module is loaded successfully, we expect it to define a
        # function called makeExtension()
        try:
            return module.makeExtension(configs.items())
        except AttributeError as e:
            message = e.args[0]
            message = "Failed to initiate extension " \
                      "'%s': %s" % (ext_name, message)
            e.args = (message,) + e.args[1:]
            raise


def markdown(text, *args, **kwargs):
    """Convert a markdown string to HTML and return HTML as a unicode string.

    This is a shortcut function for `Markdown` class to cover the most
    basic use case.  It initializes an instance of Markdown, loads the
    necessary extensions and runs the parser on the given text.

    Keyword arguments:

    * text: Markdown formatted text as Unicode or ASCII string.
    * Any arguments accepted by the Markdown class.

    Returns: An HTML document as a string.

    """
    md = StMarkdown(*args, **kwargs)
    return md.convert(text)
