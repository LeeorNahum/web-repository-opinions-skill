# Abuse Resistance

A product reachable from the open internet is a target on day one. Bound what a single caller can cost the product before finding out the hard way.

## Quota As Anti-Abuse Plumbing

Hold two different numbers, not one. A hidden internal quota, sized to the max load the product can absorb, applies to every account regardless of plan and stays invisible. A user-facing plan limit is a separate, smaller, marketing and billing number carved inside that internal ceiling, and it is the one shown.

Ship the internal quota on day one, including in a free product. A price of zero is the strongest abuse magnet a product can offer, and abuse does not wait for a paid tier to exist.

Rate limiting is a different gate from quota, and often layers on the same request. It blunts volume and cost from a caller regardless of identity, and belongs at the edge or gateway, not a product database table. Quota governs how much of the product a given account is entitled to use. Losing either leaves the other doing a job it was not sized for.

## Upload Hardening

Cap size, file count, and accepted type before bytes get far. Treat archive extraction as attacker-controlled: guard against path traversal on extraction, reject symlink entries, and cap decompression ratios.
