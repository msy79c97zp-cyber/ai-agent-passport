"""
Shared billing constants for machine-to-machine (M2M) credit tracking.

Keeping magic numbers in one place makes them easy to find and change.
"""

# Credits granted when a new agent registers.
DEFAULT_STARTING_CREDITS = 50

# Credits added when a Stripe MPP machine-wallet payment succeeds.
REFILL_CREDITS_AMOUNT = 5000

# Cost of one passport verification lookup.
VERIFICATION_CREDIT_COST = 1

# Machine-readable message returned with HTTP 402 Payment Required.
PAYMENT_REQUIRED_MESSAGE = (
    "Prepaid balance exhausted. Settle invoice via Stripe Machine "
    "Payments Protocol (MPP) to refill credits."
)
