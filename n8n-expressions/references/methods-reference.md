# Expression Methods Reference

Complete reference for all available methods in n8n expressions.

---

## Array Methods

| Method | Description | Example |
|--------|-------------|---------|
| `.length` | Number of elements | `{{$json.items.length}}` |
| `.filter(fn)` | Filter elements | `{{ $json.items.filter(i => i.active) }}` |
| `.map(fn)` | Transform elements | `{{ $json.items.map(i => i.name) }}` |
| `.find(fn)` | First matching element | `{{ $json.items.find(i => i.id === 1) }}` |
| `.reduce(fn, init)` | Reduce to single value | `{{ $json.items.reduce((s, i) => s + i.price, 0) }}` |
| `.join(sep)` | Join into string | `{{ $json.tags.join(', ') }}` |
| `.sort(fn)` | Sort array | `{{ $json.items.sort((a, b) => b.score - a.score) }}` |
| `.slice(start, end)` | Extract portion | `{{ $json.items.slice(0, 10) }}` |
| `.first()` / `.last()` | First/last element | `{{ $json.items.first() }}` |
| `.sum()` / `.min()` / `.max()` / `.average()` | Numeric operations | `{{ $json.prices.sum() }}` |
| `.removeDuplicates(keys?)` | Remove duplicates | `{{ $json.items.removeDuplicates('id') }}` |
| `.toJsonString()` | Convert to JSON string | `{{ $json.items.toJsonString() }}` |
| `.pluck(field1, field2?)` | Extract field values | `{{ $json.users.pluck('name', 'email') }}` |

---

## String Methods

| Method | Description | Example |
|--------|-------------|---------|
| `.toUpperCase()` / `.toLowerCase()` | Change case | `{{ $json.name.toUpperCase() }}` |
| `.trim()` | Remove whitespace | `{{ $json.text.trim() }}` |
| `.includes(str)` | Check contains | `{{ $json.email.includes('@') }}` |
| `.replace(pattern, replacement)` | Replace first | `{{ $json.text.replace('old', 'new') }}` |
| `.replaceAll(pattern, replacement)` | Replace all | `{{ $json.text.replaceAll('\n', '<br>') }}` |
| `.split(sep)` | Split into array | `{{ $json.tags.split(',') }}` |
| `.match(regexp)` | Regex match | `{{ $json.text.match(/\d+/) }}` |
| `.substring(start, end)` | Extract substring | `{{ $json.text.substring(0, 10) }}` |

### String Extraction & Validation

| Method | Description | Example |
|--------|-------------|---------|
| `.extractEmail()` | Extract emails | `{{ $json.text.extractEmail() }}` |
| `.extractUrl()` | Extract URLs | `{{ $json.text.extractUrl() }}` |
| `.extractDomain()` | Extract domain | `{{ $json.url.extractDomain() }}` |
| `.isEmail()` | Check if email | `{{ $json.value.isEmail() }}` |
| `.isUrl()` | Check if URL | `{{ $json.value.isUrl() }}` |
| `.isDomain()` | Check if domain | `{{ $json.value.isDomain() }}` |
| `.isNumeric()` | Check if numeric | `{{ $json.value.isNumeric() }}` |

### String Conversion

| Method | Description | Example |
|--------|-------------|---------|
| `.parseJson()` | Parse JSON string | `{{ $json.data.parseJson() }}` |
| `.toDateTime()` | Convert to DateTime | `{{ $json.date.toDateTime() }}` |
| `.toNumber()` | Convert to number | `{{ $json.value.toNumber() }}` |
| `.toBoolean()` | Convert to boolean | `{{ $json.value.toBoolean() }}` |
| `.hash(algo?)` | Hash (default: md5) | `{{ $json.text.hash('sha256') }}` |
| `.base64Encode()` / `.base64Decode()` | Base64 | `{{ $json.text.base64Encode() }}` |
| `.urlEncode()` / `.urlDecode()` | URL encoding | `{{ $json.text.urlEncode() }}` |

---

## DateTime Methods (Luxon)

| Method | Description | Example |
|--------|-------------|---------|
| `.toFormat(fmt)` | Format as string | `{{ $now.toFormat('yyyy-MM-dd') }}` |
| `.toISO()` | ISO 8601 string | `{{ $now.toISO() }}` |
| `.toLocaleString(opts)` | Localized string | `{{ $now.toLocaleString() }}` |
| `.toRelative()` | Relative representation | `{{ $now.toRelative() }}` |
| `.plus({days: 1})` | Add time | `{{ $now.plus({days: 7}) }}` |
| `.minus({hours: 2})` | Subtract time | `{{ $now.minus({hours: 24}) }}` |
| `.diffTo(other, unit)` | Difference | `{{ $now.diffTo(other, 'days') }}` |
| `.startOf(unit)` | Round to start | `{{ $now.startOf('day') }}` |
| `.endOf(unit)` | Round to end | `{{ $now.endOf('month') }}` |
| `.setZone(zone)` | Set timezone | `{{ $now.setZone('America/New_York') }}` |
| `.toLocal()` / `.toUTC()` | Convert timezone | `{{ $now.toLocal() }}` |
| `.set({month: 1})` | Set specific values | `{{ $now.set({month: 1, day: 15}) }}` |

---

## Number Methods

| Method | Description | Example |
|--------|-------------|---------|
| `.toFixed(n)` | Fixed decimals | `{{ $json.price.toFixed(2) }}` |
| `.toString()` | Convert to string | `{{ $json.count.toString() }}` |
| Math operations | `+`, `-`, `*`, `/`, `%` | `{{ $json.price * 1.1 }}` |

---

## Helper Functions

| Function | Description | Example |
|----------|-------------|---------|
| `$if(cond, trueVal, falseVal)` | Conditional | `{{ $if($json.active, 'Yes', 'No') }}` |
| `$ifEmpty(val, defaultVal)` | Default value | `{{ $ifEmpty($json.name, 'Unknown') }}` |
| `$min(n1, n2, ...)` | Minimum | `{{ $min(1, 5, 3) }}` |
| `$max(n1, n2, ...)` | Maximum | `{{ $max(1, 5, 3) }}` |
| `$jmespath(obj, expr)` | JSON query | `{{ $jmespath($json, 'users[*].name') }}` |
