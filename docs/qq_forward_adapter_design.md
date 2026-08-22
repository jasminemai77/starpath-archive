# QQ Forward Message Adapter Design

## Scope

`QQForwardMessageAdapter` converts a platform-neutral `MessagePresentation`
into a `QQForwardPayload`. It is a payload-only boundary: it does not create
AstrBot components, serialize a OneBot request, connect to NapCat, select a
recipient, or send a message.

## Verified Platform Shape

The local AstrBot v4.27.2 source exposes `Node` and `Nodes` message
components. `Nodes.to_dict()` produces a `messages` collection of node
documents. The aiocqhttp adapter detects `Node` or `Nodes`; only in its runtime
delivery path does it call OneBot's `send_group_forward_msg` or
`send_private_forward_msg`.

Each AstrBot node has a component list, while `Node.to_dict()` represents its
content as OneBot-style segment documents. Image components are converted to
base64 at that later AstrBot component boundary. This Sprint deliberately stops
before all of those operations.

## Payload Model

- `QQForwardPayload(title, nodes)` is the complete ordered forward plan.
- `QQForwardNode(node_type="text", text=...)` represents a header, section,
  or footer.
- `QQForwardNode(node_type="resource", resource=DisplayResource)` retains an
  existing image resource reference; no second image model is created.

The adapter emits nodes in this stable order:

1. title and optional subtitle as one header node;
2. ordered message sections;
3. resource references in their existing resource sequence;
4. optional footer.

An image-free message is valid and becomes text-only nodes.

## Deferred Delivery Boundary

A future delivery integration must inject forward-node sender identity and use
the appropriate AstrBot `Node`/`Nodes` component constructors. It must retain
ownership of recipient selection, component construction, image preparation,
and transport. No OneBot action name, QQ connection, or send API is imported
by this adapter.
