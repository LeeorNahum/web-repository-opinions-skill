# Abuse Resistance

A product reachable from the open internet is a target on day one. Bound what a single caller can cost the product before finding out the hard way.

## Quota As Anti-Abuse Plumbing

Hold two different numbers, not one. A hidden internal quota, sized to the max load the product can absorb, applies to every account regardless of plan and stays invisible. A user-facing plan limit is a separate, smaller, marketing and billing number carved inside that internal ceiling, and it is the one shown.

Ship the internal quota on day one, including in a free product. A price of zero is the strongest abuse magnet a product can offer, and abuse does not wait for a paid tier to exist.

Count every paid provider attempt against that internal ceiling, failed ones included, because a provider bills the product for work that charged the user's allowance nothing. Reserve against it before each attempt, record what each attempt cost, and when it stops paid work, say so in product-owned copy without showing the internal number.

Rate limiting is a different gate from quota, and often layers on the same request. It blunts volume and cost from a caller regardless of identity, and belongs at the edge or gateway, not a product database table. Quota governs how much of the product a given account is entitled to use. Losing either leaves the other doing a job it was not sized for.

## Upload Hardening

Cap size, file count, and accepted type before bytes get far. Treat archive extraction as attacker-controlled: guard against path traversal on extraction, reject symlink entries, and cap decompression ratios.

A server-side fetch of a caller-supplied URL streams with a byte cap at the file limit and a timeout, and follows a bounded number of redirects, rechecking every hop. It resolves each host, refuses loopback, private, link-local, and metadata addresses, connects only to an address that passed that check, and validates the bytes it received rather than the type it was told.
