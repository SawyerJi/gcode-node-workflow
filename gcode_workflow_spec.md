# G-code Workflow Specification

## Goal

Build a G-code workflow with two user import entries:

1. Model G-code import: the G-code generated from the original 3D model.
2. Cutting G-code import: the user-provided cutting process G-code, called `Z`.

The final execution order is:

```text
print X
wait 10s
run Z
wait 10s
print Y
```

In G-code, the 10 second waits should normally be emitted as:

```gcode
G4 S10
```

## Height Rule

Use `Z = 6mm` as the boundary.

- `A`: the model region below 6mm.
- `B`: the model region above 6mm.

The model-derived print process is split into two print parts:

- `X`: the intersection between the `A` boundary model and the `B` boundary model.
- `Y`: the remaining part of `B` after removing `X`.

Then the externally imported cutting G-code is inserted between `X` and `Y`.

## Recommended Processing Model

The most reliable workflow is geometry-first:

1. Import the original 3D model.
2. Split or classify geometry using the 6mm boundary.
3. Generate the `X` model and `Y` model.
4. Slice `X` into `X.gcode`.
5. Slice `Y` into `Y.gcode`.
6. Import user cutting G-code as `Z.gcode`.
7. Merge:

```text
X.gcode
G4 S10
Z.gcode
G4 S10
Y.gcode
```

This is preferred because true model intersection/subtraction is geometric. It is hard to recover cleanly from already-sliced G-code alone.

## Alternative Processing Model

If the only available input is already-sliced model G-code, the split can be approximated by layer height:

- `X.gcode`: commands belonging to layers at or below the interface region around `Z = 6mm`.
- `Y.gcode`: commands belonging to layers above `Z = 6mm`, excluding the part assigned to `X`.

This approach needs a precise rule for detecting the interface region, because G-code does not preserve enough information to know the true 3D boolean intersection.

## Import Entries

### Entry 1: Model G-code

User imports already-sliced model G-code. This source is used to extract:

- `X.gcode`
- `Y.gcode`

### Entry 2: Cutting G-code

User imports the cutting G-code. This is used directly as:

- `Z.gcode`

Before insertion, the workflow should optionally sanitize `Z.gcode`:

- remove startup commands that reset the printer unexpectedly
- remove end commands that turn off motors/heaters too early
- preserve motion, extrusion/cutting, feedrate, and tool commands needed by the cutting process

## Final Output Structure

```gcode
; ---- BEGIN X: model intersection print ----
... X.gcode ...
; ---- END X ----

; ---- WAIT BEFORE CUTTING ----
G4 S10

; ---- BEGIN Z: imported cutting G-code ----
... Z.gcode ...
; ---- END Z ----

; ---- WAIT BEFORE Y ----
G4 S10

; ---- BEGIN Y: remaining upper model print ----
... Y.gcode ...
; ---- END Y ----
```

## Current Decision

The first import is already-sliced model G-code, so the workflow uses G-code layer-height splitting instead of geometry boolean splitting.

Because sliced G-code does not contain complete model geometry, `X` and `Y` are approximated from toolpath Z positions:

- `X`: startup/header plus model print commands up to and including the first layer whose Z is at or above 6mm.
- `Y`: the remaining model print commands after that split point, plus the original ending/footer commands.

## Remaining Open Decisions

The following details should be fixed before production use:

1. Whether the 6mm boundary layer itself should belong to `X`, `Y`, or be duplicated/treated specially.
2. Which printer flavor is targeted, for example Bambu, Marlin, Klipper, or RepRap.
3. Whether `Z.gcode` contains its own startup/end blocks that must be stripped.
