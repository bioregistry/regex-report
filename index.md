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
        <td>{{ entry.name }}</td>
        <td><kbd>{{ entry.pattern }}</kbd></td>
        <td>{{ entry.invalid }}</td>
        <td>{{ entry.total }}</td>
        <td>{{ entry.invalid_percent }}</td>
    </tr>
{% endfor %}
</tbody>
</table>
