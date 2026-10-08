"""Bridge saved HTML observations to a trusted, offline extractor.

The extractor is supplied by application code, never loaded from request data.
The optional default is mcp-toolcall-lab's stdlib HTML extraction module.
No acquisition, asset loading, or network operation is owned here.
"""
from blueprobe import new_report


class HtmlSource:
    def __init__(self, *, selector=None, extractor=None, include_css=False, stylesheets=None):
        self.selector = selector
        self.extractor = extractor
        self.include_css = include_css
        self.stylesheets = stylesheets

    def parse(self, html, url):
        extractor = self.extractor
        if extractor is None:
            try:
                from mcp_toolcall_lab.adapters.html_snapshot import extract
            except ImportError as exc:
                raise RuntimeError(
                    'provide an offline extractor or install the source-access version of mcp-toolcall-lab'
                ) from exc
            extractor = extract
        report = new_report()
        try:
            options = {'selector': self.selector}
            if self.include_css or self.stylesheets is not None:
                options.update(include_css=self.include_css, stylesheets=self.stylesheets)
            result = extractor(html, url, **options)
        except ValueError as exc:
            report['counts']['extraction_failed'] += 1
            report['unknown'].append({'raw': html, 'url': url, 'reason': str(exc)})
            return report
        report['records'].append({'key': url, 'url': url, 'raw': html, 'derived': result})
        return report


def parse(html, url):
    """Default generic extraction for the existing BlueProbe cache CLI."""
    return HtmlSource().parse(html, url)
