"""Bridge saved HTML observations to a trusted, offline extractor.

The extractor is supplied by application code, never loaded from request data.
The optional default is mcp-toolcall-lab's stdlib HTML extraction module.
No acquisition, asset loading, or network operation is owned here.
"""
from blueprobe import new_report


class HtmlSource:
    def __init__(self, *, selector=None, extractor=None, include_css=False, stylesheets=None,
                 snapshot_extractor=None):
        self.selector = selector
        self.extractor = extractor
        self.include_css = include_css
        self.stylesheets = stylesheets
        self.snapshot_extractor = snapshot_extractor

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

    def parse_snapshot(self, snapshot):
        """Use lab's existing snapshot validation, preserving acquisition provenance.

        Cache.snapshot verifies persisted bytes first. The lab validator checks
        the snapshot envelope and decoded content, not response authenticity or
        the truth of its URL/acquisition time. A raw extractor is not a substitute
        for this separate snapshot-extractor contract.
        """
        extractor = self.snapshot_extractor
        if extractor is None:
            try:
                from mcp_toolcall_lab.source_access import extract_snapshot
            except ImportError as exc:
                raise RuntimeError(
                    'provide an offline snapshot extractor or install the source-access version of mcp-toolcall-lab'
                ) from exc
            extractor = extract_snapshot
        report = new_report()
        options = {'selector': self.selector}
        if self.include_css or self.stylesheets is not None:
            options.update(include_css=self.include_css, stylesheets=self.stylesheets)
        try:
            result = extractor(snapshot, **options)
        except ValueError as exc:
            report['counts']['extraction_failed'] += 1
            saved = snapshot if isinstance(snapshot, dict) else {}
            raw = saved.get('html', '')
            report['unknown'].append({'raw': raw if isinstance(raw, str) else '',
                                      'url': saved.get('url'), 'reason': str(exc),
                                      'snapshot': snapshot})
            return report
        report['records'].append({
            'key': snapshot['url'], 'url': snapshot['url'], 'raw': snapshot['html'],
            'derived': result['extraction'], 'snapshot': result['snapshot'],
            'cache_entry': snapshot.get('cache_entry'),
        })
        return report


def parse(html, url):
    """Default generic extraction for the existing BlueProbe cache CLI."""
    return HtmlSource().parse(html, url)


def parse_snapshot(snapshot):
    """Validate a saved html-snapshot/1 with lab before generic extraction."""
    return HtmlSource().parse_snapshot(snapshot)
