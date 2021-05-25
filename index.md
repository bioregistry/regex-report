---
layout: home
---
Generated at https://github.com/bioregistry/regex-report using the Bioregistry and PyOBO.

<table>
<thead>
<tr>
    <th>Prefix</th>
    <th>Name</th>
    <th>Pattern</th>
    <th>Invalid</th>
    <th>Total</th>
    <th>Percent</th>
</tr>
</thead>
<tbody>
{% for entry in site.data.report %}
    <tr>
        <td>{{ entry.prefix }}</td>
        <td><a href="https://bioregistry.io/{{ entry.prefix }}">{{ entry.name }}</a></td>
        <td><kbd>{{ entry.pattern }}</kbd></td>
        <td align="right">{{ entry.invalid }}</td>
        <td align="right">{{ entry.total }}</td>
        <td align="right">{{ entry.invalid_percent }}%</td>
    </tr>
{% endfor %}
</tbody>
</table>
