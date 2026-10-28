"""Render public GitHub contribution levels without a third-party image service."""
from datetime import date, timedelta
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen


class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.days = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'td' and 'data-date' in attrs and 'data-level' in attrs:
            self.days[date.fromisoformat(attrs['data-date'])] = int(attrs['data-level'])


request = Request('https://github.com/users/youssefkachmar/contributions',
                  headers={'User-Agent': 'youssefkachmar-profile'})
with urlopen(request, timeout=30) as response:
    parser = Calendar()
    parser.feed(response.read().decode())
if len(parser.days) < 300:
    raise RuntimeError('Incomplete calendar; keeping the previous graphic.')
start = min(parser.days)
start -= timedelta(days=(start.weekday() + 1) % 7)
colors = ['#1d1822', '#50182e', '#8d1e49', '#cd245f', '#ff2d78']
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="230" viewBox="0 0 960 230" role="img" aria-labelledby="title desc">',
         '<title id="title">GitHub contribution calendar</title>',
         '<desc id="desc">Public contribution intensity over the past year. Dark squares mean no contributions; brighter pink means more.</desc>',
         '<rect x="1" y="1" width="958" height="228" rx="12" fill="#0d1117" stroke="#462036"/>',
         '<g font-family="Consolas,monospace"><text x="25" y="30" fill="#ff2d78" font-size="13">CONTRIBUTIONS / PAST YEAR</text>',
         f'<text x="935" y="30" text-anchor="end" fill="#a6a9bd" font-size="11">UPDATED {max(parser.days).isoformat()}</text>']
for day, level in sorted(parser.days.items()):
    delta = (day - start).days
    week, weekday = divmod(delta, 7)
    x, y = 48 + week * 16, 65 + weekday * 16
    if day.day == 1:
        parts.append(f'<text x="{x}" y="53" fill="#a6a9bd" font-size="10">{day.strftime("%b")}</text>')
    parts.append(f'<rect x="{x}" y="{y}" width="12" height="12" rx="2" fill="{colors[level]}"><title>{day.isoformat()}: contribution level {level}/4</title></rect>')
parts.append('<text x="25" y="207" fill="#a6a9bd" font-size="10">PUBLIC ACTIVITY</text><text x="790" y="207" fill="#a6a9bd" font-size="10">LESS</text>')
for i, color in enumerate(colors):
    parts.append(f'<rect x="{822+i*16}" y="197" width="12" height="12" rx="2" fill="{color}"/>')
parts.append('<text x="910" y="207" fill="#a6a9bd" font-size="10">MORE</text></g></svg>')
Path(__file__).resolve().parents[1].joinpath('activity.svg').write_text('\n'.join(parts)+'\n', encoding='utf-8')
print(f'Rendered {len(parser.days)} contribution days.')
