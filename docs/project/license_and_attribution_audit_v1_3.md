# License and attribution audit V1.3

## Repository license

No root `LICENSE` file exists. A repository license cannot be selected implicitly because that changes downstream usage rights. The project owner must choose and add one explicitly. Until then, public source availability does not grant a general license to reuse repository code.

## Data-source attribution

The authoritative source inventory is `docs/data_sources.md` with machine-readable evidence under `data/metadata`.

- UCI Online Retail II is documented as CC BY 4.0.
- The public Instacart mirror declares CC0-1.0; upstream competition provenance remains recorded.
- The Favorita public mirror has no identified license; raw data is not redistributed by this repository.
- The M5 Zenodo distribution is recorded as open while retaining upstream competition provenance and checksum evidence.
- Dunnhumby and several Kaggle donor licenses remain marked for upstream verification rather than being inferred.

Raw donor data is ignored by Git. Donors calibrate synthetic distributions; their identifiers are not merged into canonical company entities.
