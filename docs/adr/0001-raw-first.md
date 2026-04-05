# ADR 0001: Raw-first container codec

## Status
Accepted

## Context

`Form.bin` files in the local corpus are not a single text payload. They contain
multiple records, small descriptor bodies, UTF-8 text payloads, and opaque
chunks. Some records use header fields whose semantics are not fully known.

## Decision

The first repository version is raw-first:
- parse container records deterministically
- preserve every record
- expose UTF-8 payloads as editable text artifacts
- treat undocumented fields conservatively

## Consequences

Positive:
- reliable no-op round-trip
- immediate utility for corpus inspection
- safe base for future semantic parsers

Negative:
- form semantics stay mostly opaque in v1
- some size-changing edits are rejected
- full form serializer remains future work

