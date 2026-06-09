# Frame Support Mode Decision v1

## Decision

For the current mainline branch, use:

- `frame_support_mode = "triangular_bracket"`

Keep `radial_plate` only as a comparison mode.

## Why

Compared with the radial plate option, the triangular bracket mode better matches the current launcher-head direction because:

1. load transfer is more naturally aligned with the stronger web sectors between barrel cutouts
2. the support language better matches the current triangular work-zone interpretation
3. the geometry reads as a more coherent frame-side support continuation for the head subassembly
4. it reduces the risk of the outer support reading like a flat afterthought bolted onto a radial concept

## Mainline implication

When reviewing screenshots, discussing packaging, or iterating the mainline CAD, treat the triangular bracket interpretation as the default unless a specific comparison turn explicitly reopens radial side plates.
