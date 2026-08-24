"""Step 1 - harvest DMP record metadata from the Zenodo REST API.

Each query targets a different way a DMP shows up on Zenodo, because no single
one catches them all: some are typed as data management plans, some are project
deliverables with a DMP title, some are bare .json exports from a DMP tool.
The overlap is removed later by record id.

    python scripts/01_harvest_records.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

# Field notes, all verified against the live API:
#   metadata.funding.award.program  -> "HORIZON.2.5" for Horizon Europe,
#                                      "H2020-EU..." for Horizon 2020
#   metadata.funding.funder.id      -> "00k4n6c32" European Commission (ROR),
#                                      "018mejw64" Deutsche Forschungsgemeinschaft
#   files.types                     -> file extensions present in the record
QUERIES = {
    # every record Zenodo itself types as a data management plan
    "dmp_typed": 'metadata.resource_type.id:"publication-datamanagementplan"',
    # DMP-typed records that ship a .json file - the maDMP seam
    "dmp_typed_json": ('metadata.resource_type.id:"publication-datamanagementplan" '
                       'AND files.types:json'),
    # .json files described as machine-actionable, whatever the record type
    "madmp_json": ('files.types:json AND (maDMP OR "machine-actionable" '
                   'OR "data management plan")'),
    # everything the European Commission funded that looks like a DMP
    "ec_pool": ('metadata.funding.funder.id:"00k4n6c32" AND '
                '(metadata.resource_type.id:"publication-datamanagementplan" '
                'OR metadata.title:("data management plan" OR DMP))'),
    # the same for the DFG - small on Zenodo, kept for completeness
    "dfg_pool": ('metadata.funding.funder.id:"018mejw64" AND '
                 '(metadata.resource_type.id:"publication-datamanagementplan" '
                 'OR "data management plan")'),
}


def main():
    common.ensure_dirs()
    print("harvesting %d queries (page size %d%s)"
          % (len(QUERIES), common.PAGE_SIZE, "" if common.TOKEN else ", no token"))
    grand = {}
    for name, q in QUERIES.items():
        records, _ = common.search(q)
        common.write_jsonl(os.path.join(common.RAW, name + ".jsonl"), records)
        for r in records:
            grand[str(r["id"])] = r
    print("unique records across all queries: %d" % len(grand))


if __name__ == "__main__":
    main()
