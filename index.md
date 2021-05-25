---
layout: home
---
<table>
<thead>
<tr>
    <th>Prefix</th>
    <th>Invalid</th>
    <th>Total</th>
    <th>Percent</th>
</tr>
</thead>
<tbody>
{% for entry in site.data.report %}
    <tr>
        <td>{{ entry.prefix }}</td>
        <td>{{ entry.invalid }}</td>
        <td>{{ entry.total }}</td>
        <td>{{ 100 * entry.invalid / entry.total }}</td>
    </tr>
{% endfor %}
</tbody>
</table>
