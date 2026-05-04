# BPMN Rules

Use BPMN for business processes, approvals, handoffs, exception paths, and cross-role workflows.

## Core notation

- Start events: thin circle.
- End events: thick circle.
- Tasks: rounded rectangles named with verb + object.
- Exclusive gateways: diamond with X or clear branch labels.
- Parallel gateways: diamond with plus sign.
- Pools and lanes: use when more than one participant, role, or department exists.
- Sequence flow: solid arrows within a pool.
- Message flow: dashed arrows between pools.

## Modeling rules

- Every process should have at least one start and one end event.
- Gateways must have explicit branch labels.
- Avoid decorative BPMN; each symbol must carry process meaning.
- Put the main path left-to-right or top-to-bottom.
- Put rejection, exception, timeout, or escalation paths on secondary lanes/branches.

## Naming

Good task names:

- `Receber solicitação`
- `Validar documentos`
- `Aprovar cadastro`
- `Enviar notificação`

Poor task names:

- `Cadastro`
- `Validação`
- `Sistema`
