# Outer Rotor Length Comparison v1

## Scope

Compare the current launcher-head packaging impact of three short/long 63-series motor lengths using the same `63mm` body diameter and the same ring-centered concept.

## Compared presets

- `6354` → `53.5mm`
- `6360` → `60mm`
- `6374` → `74mm`

## Mechanical comparison summary

| Preset | Packaging | Bottom-face support clearance | Barrel / ring friendliness | Current recommendation |
|---|---|---|---|---|
| `6354` | Best | Best | Best | **Preferred** |
| `6360` | Acceptable | Acceptable | Acceptable | Backup |
| `6374` | Worst | Tightest | Worst | Do not prioritize |

## Reasoning

### 6354

- shortest motor body in the current comparison
- easiest to keep away from adjacent support structures
- smallest tail intrusion below the ring zone
- easiest to combine with bottom-face mounting and 3 cutout ring concept

### 6360

- still workable if 6354 vendor / power / KV selection becomes problematic
- requires more care on bottom support packaging
- still materially easier than 6374

### 6374

- long body creates the worst tail interference risk
- makes ring-adjacent support layout more crowded
- increases penalty when using bottom-face mounting only
- reduces flexibility around ring cutout geometry and remaining structural webs

## Current recommendation

For the frozen concept branch — central ring, 3 cutouts, outer shell direct ball contact, bottom-face mounting — prioritize `6354` first, keep `6360` as fallback, and treat `6374` as the least favorable packaging option.
