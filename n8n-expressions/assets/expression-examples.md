# Expression Examples

Real-world expression examples for common n8n scenarios.

---

## Example 1: Webhook to Slack

**Webhook receives:**
```json
{ "body": { "name": "John Doe", "email": "john@example.com", "message": "Hello!" } }
```

**In Slack node text field:**
```
New form submission!

Name: {{$json.body.name}}
Email: {{$json.body.email}}
Message: {{$json.body.message}}
```

---

## Example 2: HTTP Request to Email

**HTTP Request returns:**
```json
{ "data": { "items": [{"name": "Product 1", "price": 29.99}] } }
```

**In Email node:**
```
Product: {{$node["HTTP Request"].json.data.items[0].name}}
Price: ${{$node["HTTP Request"].json.data.items[0].price}}
```

---

## Example 3: Conditional Content

```javascript
// Ternary operator
{{$json.status === 'active' ? 'Active User' : 'Inactive User'}}

// Default values
{{$json.email || 'no-email@example.com'}}

// Nested conditionals
{{$json.status === 'paid' ? 'Receipt sent' : $json.status === 'pending' ? 'Reminder sent' : 'Unknown status'}}
```

---

## Example 4: Date Formatting

```javascript
// Current date
{{$now.toFormat('yyyy-MM-dd')}}          // "2024-01-15"
{{$now.toFormat('HH:mm:ss')}}            // "14:30:45"
{{$now.toFormat('yyyy-MM-dd HH:mm')}}    // "2024-01-15 14:30"

// Relative dates
{{$now.plus({days: 7}).toFormat('yyyy-MM-dd')}}   // 7 days from now
{{$now.minus({hours: 24}).toISO()}}               // 24 hours ago

// Difference
{{ DateTime.fromISO($json.end_date).diff(DateTime.fromISO($json.start_date), 'days').days }}
```

---

## Example 5: String Manipulation

```javascript
// Substring
{{$json.email.substring(0, 5)}}

// Replace
{{$json.message.replace('old', 'new')}}

// Split and join
{{$json.tags.split(',').join(', ')}}

// Case conversion
{{$json.name.toUpperCase()}}
{{$json.email.toLowerCase()}}

// Trim
{{$json.input.trim()}}
```

---

## Example 6: Array Operations

```javascript
// First item
{{$json.users[0].email}}

// Array length
{{$json.users.length}}

// Last item
{{$json.users[$json.users.length - 1].name}}

// Map (extract field)
{{$json.users.map(u => u.name).join(', ')}}

// Filter
{{$json.users.filter(u => u.active).length}}

// Reduce (sum)
{{$json.items.reduce((sum, i) => sum + i.price, 0)}}
```

---

## Example 7: IIFE (Multi-Statement)

```javascript
{{(()=>{
  const end = DateTime.fromISO('2017-03-13');
  const start = DateTime.fromISO('2017-02-13');
  const diffInMonths = end.diff(start, 'months');
  return diffInMonths.toObject();
})()}}
```

---

## Example 8: $fromAI() in Tools

```javascript
// HTTP Request Tool URL
https://api.example.com/users/{{ $fromAI('userId', 'The user ID to look up', 'string') }}

// Email body
Hello {{ $fromAI('userName', "The user's name") }},
Your order {{ $fromAI('orderId', "The order ID") }} has been processed.
```

---

## Example 9: $tool in Human Review

```
The AI wants to use {{ $tool.name }} with the following parameters:
{{ JSON.stringify($tool.parameters, null, 2) }}

Do you approve this action?
```

---

## Example 10: Combining Multiple Sources

```javascript
// Merging data from webhook and API call
{
  "customer": "{{$json.body.name}}",
  "email": "{{$json.body.email}}",
  "enriched_company": "{{$node['Clearbit'].json.data.company.name}}",
  "processed_at": "{{$now.toISO()}}",
  "workflow_id": "{{$workflow.id}}"
}
```
