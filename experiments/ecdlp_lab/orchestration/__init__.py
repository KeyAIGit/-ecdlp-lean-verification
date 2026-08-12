"""Safe, deterministic orchestration for the ECDLP engineering lab.

The package root intentionally exports no filesystem or worker entry point.
Callers import the narrow pure/event, storage, runner, or worker module they
actually require.
"""

__all__: tuple[str, ...] = ()

