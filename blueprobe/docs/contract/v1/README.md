# BlueProbe contract v1

Status: **stable** (first release 1.0.0)

The compatibility surface between BlueProbe and its users (Aoi's QueRyu and SakAnalytics, and each repository).
How it is decided follows [web-ui contract/v1](https://github.com/myon-bioinformatics/web-ui/tree/main/contract/v1).

## Stability promise

- Within v1, stable items are **not removed and their meaning is not changed**
- Items may be added within v1 (readers ignore items they don't know)
- Removal, change of meaning, or making something required creates a new `docs/contract/v2/` as v2
- Patch numbers are not used as compatibility markers. The unit of compatibility is `v1` / `v2`

| Document | Covers |
|---|---|
| [report.md](report.md) | The result of reading one page (records / counts / unknown) and summary rows |
| [snapshot.md](snapshot.md) | Suppliers of saved bodies and the `html-snapshot/1` record |
