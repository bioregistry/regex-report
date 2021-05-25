# -*- coding: utf-8 -*-

"""Build the regex report."""

import datetime
import pathlib
from typing import List, Tuple, Union

import click
import pandas as pd
import yaml
from more_click import verbose_option
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

import bioregistry
import pyobo
from bioregistry.version import VERSION as BIOREGISTRY_VERSION

HERE = pathlib.Path(__file__).parent.resolve()
DATA = HERE.joinpath('_data')
DATA.mkdir(parents=True, exist_ok=True)

SKIP = {
    'gaz', 'ncbigene', 'pubchem.compound', 'pubchem.substance'
}
SKIP_PREFIX = {
    'kegg'
}
COLUMNS = ['prefix', 'invalid', 'total']


@click.command()
@verbose_option
def main():
    """Build the regex report."""
    data = []
    it = tqdm(bioregistry.read_registry(), desc='Calculating consistencies', unit='prefix')
    for prefix in it:
        it.set_postfix(prefix=prefix)
        if prefix in SKIP or any(prefix.startswith(p) for p in SKIP_PREFIX):
            continue
        with logging_redirect_tqdm():
            invalid, total = calculate(prefix)
        if invalid is None or total is None:
            continue
        data.append((prefix, invalid, total))

    # sort by invalid (desc) then prefix (asc)
    data = sorted(data, key=lambda p: (-len(p[1]), p[0]))

    df = pd.DataFrame(columns=COLUMNS, data=[
        (prefix, len(invalid), total)
        for prefix, invalid, total in data
    ])
    df.to_csv(DATA / 'report_table.tsv', sep='\t', index=False)

    with DATA.joinpath('report.yml').open('w') as file:
        yaml.safe_dump(stream=file, data=dict(
            metadata=dict(
                date=datetime.datetime.now().isoformat(),
                pyobo_version=pyobo.get_version(with_git_hash=True),
                bioregistry_version=BIOREGISTRY_VERSION,
            ),
            data=[
                dict(
                    prefix=prefix,
                    name=bioregistry.get_name(prefix),
                    version=bioregistry.get_version(prefix),
                    pattern=bioregistry.get_pattern(prefix),
                    invalid=len(invalid),
                    invalid_percent=round(100 * len(invalid) / total, 2),
                    total=total,
                    invalid_sample=invalid[:75],
                )
                for prefix, invalid, total in data
            ],
        ))


def calculate(prefix: str) -> Union[Tuple[List[str], int], Tuple[None, None]]:
    """Calculate the inconsistency for the given prefix."""
    pattern = bioregistry.get_pattern(prefix)
    if not pattern:
        return None, None
    try:
        identifiers = pyobo.get_id_name_mapping(prefix)
    except Exception:
        return None, None

    invalid = []
    for identifier in tqdm(identifiers, leave=False):
        if not bioregistry.validate(prefix, identifier):
            invalid.append(identifier)

    n_identifiers = len(identifiers)
    if n_identifiers == 0:
        echo(f'{prefix} no identifiers', fg='yellow')
        return None, None

    n_invalid = len(invalid)
    if n_invalid == 0:
        echo(f'{prefix} consistent pattern {pattern}', fg='green')
    else:
        echo(f'{prefix} had {n_invalid} ({n_invalid / n_identifiers:.2%}) invalid', fg='yellow')
    return invalid, len(identifiers)


def echo(*args, **kwargs) -> None:
    """Write with :func:`click.secho` under the tqdm lock."""
    with tqdm.external_write_mode():
        click.secho(*args, **kwargs)


if __name__ == '__main__':
    main()
