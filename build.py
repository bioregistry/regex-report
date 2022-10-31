# -*- coding: utf-8 -*-

"""Build the regex report."""

import datetime
import pathlib
from typing import Any, List, Mapping, Tuple, Union

import bioregistry
import click
import pandas as pd
import pyobo
import yaml
from bioregistry.version import VERSION as BIOREGISTRY_VERSION
from more_click import verbose_option
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

HERE = pathlib.Path(__file__).parent.resolve()
DATA = HERE.joinpath("_data")
DATA.mkdir(parents=True, exist_ok=True)
RESULTS = HERE.joinpath("results")
RESULTS.mkdir(parents=True, exist_ok=True)

SKIP = {
    "gaz",
    "ncbigene",
    "pubchem.compound",
    "pubchem.substance",
    "umls",
    "antibodyregistry",
    "ncit",
    "mesh",
}
SKIP_PREFIX = {"kegg"}
COLUMNS = ["prefix", "invalid", "total", "percent_invalid"]
DICT_COLS = ["identifier", "name", "link"]


@click.command()
@verbose_option
@click.option("--single")
def main(single: str):
    """Build the regex report."""
    results = []
    prefixes = [
        prefix
        for prefix, resource in bioregistry.read_registry().items()
        if (
            resource.get_pattern() is not None
            and prefix not in SKIP
            and not any(prefix.startswith(p) for p in SKIP_PREFIX)
        )
    ]
    if single:
        prefixes = [single]
    it = tqdm(prefixes, desc="Calculating consistencies", unit="prefix")
    for prefix in it:
        it.set_postfix(prefix=prefix)
        with logging_redirect_tqdm():
            invalid, total = calculate(prefix)
        path = RESULTS.joinpath(prefix).with_suffix(".tsv")
        if not invalid or not total:
            if path.is_file():
                path.unlink()
            continue
        invalid_df = pd.DataFrame(invalid, columns=["identifier", "name", "link"])
        invalid_df.to_csv(path, sep="\t", index=False)
        results.append((prefix, invalid, total))

    if single:
        return

    # sort by invalid (desc) then prefix (asc)
    results = sorted(results, key=lambda p: (-len(p[1]), p[0]))

    df = pd.DataFrame(
        columns=COLUMNS,
        data=[
            (
                prefix,
                len(invalid),
                total,
                len(invalid) / total if total > 0 else None,
            )
            for prefix, invalid, total in results
        ],
    )
    df.to_csv(DATA / "report_table.tsv", sep="\t", index=False)

    dump_data = sorted(
        [
            dict(
                prefix=prefix,
                name=bioregistry.get_name(prefix),
                version=bioregistry.get_version(prefix),
                pattern=bioregistry.get_pattern(prefix),
                invalid=len(invalid),
                invalid_percent=round(100 * len(invalid) / total, 2),
                total=total,
                invalid_sample=[dict(zip(DICT_COLS, row)) for row in invalid[:25]],
            )
            for prefix, invalid, total in results
        ],
        key=lambda entry: (-entry["invalid_percent"], entry["invalid"]),
    )

    with DATA.joinpath("report.yml").open("w") as file:
        yaml.safe_dump(
            stream=file,
            data=dict(
                metadata=dict(
                    date=datetime.datetime.now().isoformat(),
                    pyobo_version=pyobo.get_version(with_git_hash=True),
                    bioregistry_version=BIOREGISTRY_VERSION,
                ),
                data=dump_data,
            ),
        )


def calculate(
    prefix: str,
) -> Union[Tuple[List[Mapping[str, Any]], int], Tuple[None, None]]:
    """Calculate the inconsistency for the given prefix."""
    resource = bioregistry.get_resource(prefix)
    pattern = resource.get_pattern_re()
    if not pattern:
        return None, None
    try:
        identifiers = pyobo.get_ids(prefix)
    except Exception:
        return None, None

    invalid = []
    for identifier in tqdm(
        identifiers,
        leave=False,
        unit_scale=True,
        unit="identifier",
        desc=f"Validating {prefix}",
    ):
        if not pattern.fullmatch(identifier):
            invalid.append(
                (
                    identifier,
                    pyobo.get_name(prefix, identifier),
                    bioregistry.get_iri(prefix, identifier),
                )
            )

    n_identifiers = len(identifiers)
    if n_identifiers == 0:
        echo(f"{prefix} no identifiers", fg="yellow")
        return None, None

    n_invalid = len(invalid)
    if n_invalid == 0:
        echo(f"{prefix} consistent pattern {pattern}", fg="green")
    elif n_invalid == len(identifiers):
        echo(f"{prefix} fully inconsistent pattern {pattern}", fg="red")
    else:
        echo(
            f"{prefix} had {n_invalid} ({n_invalid / n_identifiers:.2%}) invalid",
            fg="yellow",
        )
    return sorted(invalid), len(identifiers)


def echo(*args, **kwargs) -> None:
    """Write with :func:`click.secho` under the tqdm lock."""
    with tqdm.external_write_mode():
        click.secho(*args, **kwargs)


if __name__ == "__main__":
    main()
