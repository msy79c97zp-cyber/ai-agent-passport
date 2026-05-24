"""Read-only ledger statistics for the public storefront."""

from supabase import Client

AGENTS_TABLE = "agents"


class StatsService:
    """Fetches aggregate counts from the agent ledger."""

    def __init__(self, client: Client) -> None:
        self.client = client

    def count_verified_active_agents(self) -> int:
        """
        Return agents with active passports on the ledger.

        Counts `is_active=true` rows — the live number developers expect
        to see grow as agents register.
        """
        response = (
            self.client.table(AGENTS_TABLE)
            .select("id", count="exact")
            .eq("is_active", True)
            .execute()
        )
        return response.count or 0
