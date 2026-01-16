"""
Base protocol definitions voor alle services.

We gebruiken Protocol i.p.v. ABC omdat:
- Lichter dan abstracte classes
- Duck typing - geen inheritance nodig
- Makkelijk te mocken voor tests
"""
from typing import Protocol, runtime_checkable


@runtime_checkable
class HealthCheckable(Protocol):
    """Protocol voor services die health checks ondersteunen."""

    async def health_check(self) -> bool:
        """
        Check of de service beschikbaar is.

        Returns:
            True als service beschikbaar, False anders
        """
        ...
