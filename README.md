# vox

salt + key → a new band80, always the same for the same pair.

```
$ vox 25018599682202377746.87783789576741058797.28832678037307446403.33471880386520197097
key:
67137111632918228090.03198478452534193697.85614958450118272798.55305506750949179189
```

No dependencies. One function. Nothing stored.

## Install

```
pip install git+https://github.com/mrtatiso/vox
```

## Use

### Terminal

```
vox <salt>
```

The key is asked without showing it. It is never passed as an argument, so it does not end up in the shell history. From a script it can come through stdin:

```
echo "holamundo" | vox <salt>
```

### Python

```python
from vox import vox

vox(salt, "holamundo")
```

`vox` raises `ValueError` if the salt does not have exactly 80 digits.

## What it does

- **Any key works.** There is no wrong key: every key gives a valid band80. The same salt and key always give the same one.
- **The salt is any 80 digits**, usually from [band80](https://github.com/mrtatiso/band80). vox never generates anything random.
- **The grouping follows the salt.** A 4:20 salt gives a 4:20 vox, an 80:1 salt an 80:1 vox. Only the digits enter the calculation, so the same salt in any grouping gives the same digits.
- **Each derivation costs memory on purpose:** 64 MiB and a fraction of a second. Fine for one login, expensive for someone trying millions of keys.

## v1

| | |
|---|---|
| function | scrypt, N = 2¹⁶, r = 8, p = 1 (64 MiB) |
| key | Unicode NFC, UTF-8 |
| salt | `vox1|` + the 80 digits |
| output | 80 uniform digits added to the salt, digit by digit, mod 10 |

These never change within v1. Changing any of them changes every vox, so it would be v2. The tests include fixed answers that any implementation of v1, in any language, must reproduce.

## Test

```
python -m unittest discover test
```

## Verify

```
sha256sum vox.py
```

v1.0.0:

```
30969691d2a35e203662336681476120edc8524a4d7f9e7e0fa46beab398d128
```
