#!/usr/bin/env python3
"""vox: salt + key → a new band80, always the same for the same pair.

    $ vox 39563319081286831671.85130815965080617505.81064959590150397768.12816156932300764448
    key:
    48210557390184466021.07734512980265531477.90016623458871204356.66129830147752908113

    >>> from vox import vox
    >>> vox(salt, key)

The salt is any 80 digits (usually from band80). The result keeps the salt's
grouping: a 4:20 salt gives a 4:20 vox, an 80:1 salt gives an 80:1 vox.
Only the digits enter the calculation, never the separators.

v1: scrypt (N=2^16, r=8, p=1, 64 MiB per derivation), key normalized to NFC.
Changing any of this changes every vox, so it would be v2.
"""
import getpass
import hashlib
import sys
import unicodedata

__version__ = "1.0.0"
__all__ = ["vox"]

DIGITS = 80
N, R, P = 2 ** 16, 8, 1
MEMORY = 128 * N * R  # 64 MiB


def _stream(seed: bytes):
    """Uniform digits from a seed: bytes 0-249 → digit, 250-255 skipped."""
    out, block = [], 0
    while len(out) < DIGITS:
        for b in hashlib.shake_256(seed + block.to_bytes(4, "big")).digest(128):
            if b < 250 and len(out) < DIGITS:
                out.append(b % 10)
        block += 1
    return out


def vox(salt: str, key: str) -> str:
    """The vox for this salt and key, written with the salt's grouping."""
    digits = [int(c) for c in salt if c in "0123456789"]
    if len(digits) != DIGITS:
        raise ValueError(f"salt must have {DIGITS} digits, not {len(digits)}")
    seed = hashlib.scrypt(
        unicodedata.normalize("NFC", key).encode(),
        salt=b"vox1|" + bytes(c + 48 for c in digits),
        n=N, r=R, p=P, maxmem=MEMORY + 2 ** 24, dklen=64,
    )
    k = iter((d + s) % 10 for d, s in zip(digits, _stream(seed)))
    return "".join(str(next(k)) if c in "0123456789" else c for c in salt)


def main(args=None) -> int:
    args = sys.argv[1:] if args is None else args
    if len(args) != 1:
        print("usage: vox <salt>    (the key is asked, never passed as an argument)", file=sys.stderr)
        return 2
    key = getpass.getpass("key: ") if sys.stdin.isatty() else sys.stdin.readline().rstrip("\n")
    try:
        print(vox(args[0], key))
    except ValueError as e:
        print(f"vox: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
