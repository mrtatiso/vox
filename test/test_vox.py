import io
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout

import vox

SALT = "25018599682202377746.87783789576741058797.28832678037307446403.33471880386520197097"

# Fixed answers for vox v1. If any of these changes, it is no longer v1.
VECTORS = [
    ("0" * 80, "",
     "50512985663070910388690653493388016552844087030810765018551567088806639569495245"),
    ("12345678901234567890.12345678901234567890.12345678901234567890.12345678901234567890", "café",
     "65786956593128643054.42684543530311367367.69271550166343354957.75404101515838452029"),
    (SALT, "holamundo",
     "67137111632918228090.03198478452534193697.85614958450118272798.55305506750949179189"),
]


class TestVox(unittest.TestCase):
    def test_vectors_v1(self):
        for salt, key, expected in VECTORS:
            self.assertEqual(vox.vox(salt, key), expected)

    def test_grouping_is_kept_and_ignored(self):
        flat = SALT.replace(".", "")
        one = ".".join(flat)
        a, b = vox.vox(SALT, "holamundo"), vox.vox(one, "holamundo")
        self.assertEqual(len(b.split(".")), 80)
        self.assertEqual(a.replace(".", ""), b.replace(".", ""))

    def test_key_is_normalized(self):
        self.assertEqual(vox.vox(SALT, "café"), vox.vox(SALT, "café"))

    def test_rejects_bad_salt(self):
        for salt in (SALT[:-1], "٣" * 80, ""):
            with self.assertRaises(ValueError):
                vox.vox(salt, "x")


class TestCli(unittest.TestCase):
    def run_cli(self, args, stdin=""):
        out, err, old = io.StringIO(), io.StringIO(), sys.stdin
        sys.stdin = io.StringIO(stdin)
        try:
            with redirect_stdout(out), redirect_stderr(err):
                code = vox.main(args)
        finally:
            sys.stdin = old
        return code, out.getvalue(), err.getvalue()

    def test_key_from_stdin(self):
        code, out, _ = self.run_cli([SALT], "holamundo\n")
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), VECTORS[2][2])

    def test_usage(self):
        for args in ([], [SALT, "holamundo"]):
            code, out, err = self.run_cli(args)
            self.assertEqual(code, 2)
            self.assertIn("usage: vox", err)

    def test_bad_salt(self):
        code, _, err = self.run_cli(["123"], "x\n")
        self.assertEqual(code, 2)
        self.assertIn("80 digits", err)


if __name__ == "__main__":
    unittest.main()
