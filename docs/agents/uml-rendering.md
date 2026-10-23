# UML rendering in this repo

## Local renderer

- Status: verified locally on 2026-10-23; probe again on each UML invocation.
- Command: `plantuml`, resolving to the contributor's local wrapper or installation.
- Verified renderer: PlantUML 1.2024.8 with OpenJDK 25.0.4.101.
- Sequence diagrams use the built-in sequence layout. The installation component view uses bundled Smetana, selected in its source, without requiring Graphviz.
- Verified font: Segoe UI; contributors may substitute an available readable font.

## Commands

Inspect the active renderer with `plantuml -version`.

Render SVG: `plantuml -charset UTF-8 -failfast2 -tsvg <source.puml>`.

Render PNG from the same source: `plantuml -charset UTF-8 -failfast2 -tpng <source.puml>`.

Use local rendering and inspect the generated preview. Machine-specific executable or JAR locations belong in the contributor's local setup rather than this shared configuration.

## Verification

The setup probe exercised a sequence diagram with an optional branch. The specification preparation also rendered and inspected the workflow sequence and Smetana component views in both SVG and PNG.

Use the UML skill for source authority, preview inspection, acceptance, recovery, and external-renderer authorization requirements. This record does not replace its per-invocation check.
