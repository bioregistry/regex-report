---
layout: home
---
Generated using the Bioregistry v{{ site.data.report.metadata.bioregistry_version }}
and PyOBO v{{ site.data.report.metadata.pyobo_version }}
on {{ site.data.report.metadata.date }} using code on [GitHub](https://github.com/bioregistry/regex-report).

<table>
<thead>
<tr>
    <th>Prefix</th>
    <th>Name</th>
    <th>Version</th>
    <th>Pattern</th>
    <th>Invalid</th>
    <th>Total</th>
    <th>Percent</th>
</tr>
</thead>
<tbody>
{% for entry in site.data.report.data %}
    <tr>
        <td>{{ entry.prefix }}</td>
        <td><a href="https://bioregistry.io/{{ entry.prefix }}">{{ entry.name }}</a></td>
        <td>{{ entry.version }}</td>
        <td><kbd>{{ entry.pattern }}</kbd></td>
        <td align="right">{{ entry.invalid }}</td>
        <td align="right">{{ entry.total }}</td>
        <td align="right">{{ entry.invalid_percent }}%</td>
    </tr>
{% endfor %}
</tbody>
</table>
