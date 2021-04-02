#!/usr/bin/env python
"""CLI for NUT supervisor"""

import click
from nut_supervisor import NutSupervisor

@click.group()
@click.pass_context
def cli(ctx: click.Context):
    """Grouping item for the cli"""
    ctx.ensure_object(dict)

@cli.command("start")
@click.option("-m", "-c", "--monitor", "--cycle",
              "monitor_cycle",
              default=250,
              type=int,
              help="Monitor time in milliseconds")
@click.pass_context
def start(ctx: click.Context, monitor_cycle: int): #pylint: disable=unused-argument
    """Fire up the supervisor of the nut drivers"""
    supervisor = NutSupervisor(monitor_cycle)
    supervisor.run()

if __name__ == "__main__":
    cli() #pylint: disable=no-value-for-parameter
