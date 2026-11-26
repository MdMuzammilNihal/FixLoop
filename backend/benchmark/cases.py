"""Benchmark cases: small buggy Python programs, each with a hidden test and a reference fix.

kind="crash": the snippet's own demo call at the bottom raises or fails to parse, so *running* the
              code reveals the bug (execution feedback can help the model).
kind="logic": the snippet runs fine but returns wrong results, so only the hidden test reveals it
              (execution feedback cannot help).

A fix PASSES when ``fixed_code + test`` runs with exit code 0. The model never sees the tests.
"""

CASES = []


def case(id, kind, buggy, test, reference):
    CASES.append({
        "id": id,
        "kind": kind,
        "buggy": buggy.strip("\n"),
        "test": test.strip("\n"),
        "reference": reference.strip("\n"),
    })


# ----------------------------------------------------------------------------- crash bugs (20)

case("avg_empty", "crash", """
def avg(nums):
    return sum(nums) / len(nums)

print(avg([]))
""", """
assert avg([1, 2, 3]) == 2
""", """
def avg(nums):
    return sum(nums) / len(nums) if nums else 0

print(avg([]))
""")

case("last_item", "crash", """
def last(xs):
    return xs[len(xs)]

print(last([1, 2, 3]))
""", """
assert last([1, 2, 3]) == 3
""", """
def last(xs):
    return xs[-1]

print(last([1, 2, 3]))
""")

case("dict_missing_key", "crash", """
def get_age(person):
    return person["age"]

print(get_age({"name": "Sam"}))
""", """
assert get_age({"age": 5}) == 5
get_age({"name": "Sam"})
""", """
def get_age(person):
    return person.get("age")

print(get_age({"name": "Sam"}))
""")

case("name_typo", "crash", """
def total(prices):
    s = 0
    for p in prices:
        ss += p
    return s

print(total([1, 2, 3]))
""", """
assert total([1, 2, 3]) == 6
""", """
def total(prices):
    s = 0
    for p in prices:
        s += p
    return s

print(total([1, 2, 3]))
""")

case("str_plus_int", "crash", """
def greet(name, age):
    return "Hi " + name + ", you are " + age

print(greet("Ann", 30))
""", """
assert greet("Ann", 30) == "Hi Ann, you are 30"
""", """
def greet(name, age):
    return "Hi " + name + ", you are " + str(age)

print(greet("Ann", 30))
""")

case("missing_colon", "crash", """
def square(x)
    return x * x

print(square(3))
""", """
assert square(4) == 16
""", """
def square(x):
    return x * x

print(square(3))
""")

case("unclosed_paren", "crash", """
def add(a, b):
    return (a + b

print(add(1, 2))
""", """
assert add(2, 3) == 5
""", """
def add(a, b):
    return (a + b)

print(add(1, 2))
""")

case("bad_indent", "crash", """
def inc(x):
return x + 1

print(inc(1))
""", """
assert inc(1) == 2
""", """
def inc(x):
    return x + 1

print(inc(1))
""")

case("divide_by_zero", "crash", """
def ratio(a, b):
    return a / b

print(ratio(1, 0))
""", """
assert ratio(6, 3) == 2
ratio(1, 0)
""", """
def ratio(a, b):
    return a / b if b else None

print(ratio(1, 0))
""")

case("first_word_empty", "crash", """
def first_word(s):
    return s.split()[0]

print(first_word(""))
""", """
assert first_word("hello world") == "hello"
first_word("")
""", """
def first_word(s):
    parts = s.split()
    return parts[0] if parts else ""

print(first_word(""))
""")

case("int_parse", "crash", """
def to_int(s):
    return int(s)

print(to_int("abc"))
""", """
assert to_int("12") == 12
to_int("abc")
""", """
def to_int(s):
    try:
        return int(s)
    except ValueError:
        return None

print(to_int("abc"))
""")

case("missing_file", "crash", """
def read_lines(path):
    with open(path) as f:
        return f.readlines()

print(read_lines("definitely_missing_file.txt"))
""", """
import os, tempfile
p = os.path.join(tempfile.mkdtemp(), "a.txt")
with open(p, "w") as f:
    f.write("x\\ny\\n")
assert read_lines(p) == ["x\\n", "y\\n"]
read_lines("definitely_missing_file.txt")
""", """
def read_lines(path):
    try:
        with open(path) as f:
            return f.readlines()
    except FileNotFoundError:
        return []

print(read_lines("definitely_missing_file.txt"))
""")

case("factorial_no_base", "crash", """
def fact(n):
    return n * fact(n - 1)

print(fact(5))
""", """
assert fact(5) == 120
assert fact(0) == 1
""", """
def fact(n):
    return 1 if n <= 1 else n * fact(n - 1)

print(fact(5))
""")

case("pairs_index", "crash", """
def pairs(xs):
    return [(xs[i], xs[i + 1]) for i in range(len(xs))]

print(pairs([1, 2, 3]))
""", """
assert pairs([1, 2, 3]) == [(1, 2), (2, 3)]
""", """
def pairs(xs):
    return [(xs[i], xs[i + 1]) for i in range(len(xs) - 1)]

print(pairs([1, 2, 3]))
""")

case("initials_double_space", "crash", """
def initials(name):
    return "".join(w[0] for w in name.split(" "))

print(initials("John  Smith"))
""", """
assert initials("John Smith") == "JS"
assert initials("John  Smith") == "JS"
""", """
def initials(name):
    return "".join(w[0] for w in name.split())

print(initials("John  Smith"))
""")

case("counter_keyerror", "crash", """
def count_words(text):
    counts = {}
    for w in text.split():
        counts[w] += 1
    return counts

print(count_words("a b a"))
""", """
assert count_words("a b a") == {"a": 2, "b": 1}
""", """
def count_words(text):
    counts = {}
    for w in text.split():
        counts[w] = counts.get(w, 0) + 1
    return counts

print(count_words("a b a"))
""")

case("import_typo", "crash", """
def hypot(a, b):
    import maths
    return maths.sqrt(a * a + b * b)

print(hypot(3, 4))
""", """
assert hypot(3, 4) == 5.0
""", """
def hypot(a, b):
    import math
    return math.sqrt(a * a + b * b)

print(hypot(3, 4))
""")

case("nested_key", "crash", """
def city(d):
    return d["address"]["city"]

print(city({"address": {}}))
""", """
assert city({"address": {"city": "Lahore"}}) == "Lahore"
city({"address": {}})
""", """
def city(d):
    return d.get("address", {}).get("city")

print(city({"address": {}}))
""")

case("append_returns_none", "crash", """
def squares(n):
    out = []
    for i in range(n):
        out = out.append(i * i)
    return out

print(squares(3))
""", """
assert squares(4) == [0, 1, 4, 9]
""", """
def squares(n):
    out = []
    for i in range(n):
        out.append(i * i)
    return out

print(squares(3))
""")

case("tuple_assignment", "crash", """
def swap(t):
    t[0], t[1] = t[1], t[0]
    return t

print(swap((1, 2)))
""", """
assert tuple(swap((1, 2))) == (2, 1)
""", """
def swap(t):
    return (t[1], t[0])

print(swap((1, 2)))
""")

# ----------------------------------------------------------------------------- logic bugs (20)

case("max_negatives", "logic", """
def find_max(xs):
    m = 0
    for x in xs:
        if x > m:
            m = x
    return m

print(find_max([3, 9, 2]))
""", """
assert find_max([-3, -1, -2]) == -1
assert find_max([3, 9, 2]) == 9
""", """
def find_max(xs):
    m = xs[0]
    for x in xs:
        if x > m:
            m = x
    return m

print(find_max([3, 9, 2]))
""")

case("is_even_inverted", "logic", """
def is_even(n):
    return n % 2 == 1

print(is_even(4))
""", """
assert is_even(2) and not is_even(3)
""", """
def is_even(n):
    return n % 2 == 0

print(is_even(4))
""")

case("fib_off_by_one", "logic", """
def fib(n):
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return a

print(fib(10))
""", """
assert fib(10) == 55
assert fib(1) == 1
assert fib(0) == 0
""", """
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

print(fib(10))
""")

case("reverse_drops_char", "logic", """
def reverse_string(s):
    return s[1:][::-1]

print(reverse_string("hello"))
""", """
assert reverse_string("hello") == "olleh"
""", """
def reverse_string(s):
    return s[::-1]

print(reverse_string("hello"))
""")

case("palindrome_odd", "logic", """
def is_palindrome(s):
    half = len(s) // 2
    return s[:half] == s[half:][::-1]

print(is_palindrome("abba"))
""", """
assert is_palindrome("aba")
assert is_palindrome("abba")
assert not is_palindrome("abc")
""", """
def is_palindrome(s):
    return s == s[::-1]

print(is_palindrome("abba"))
""")

case("sum_to_exclusive", "logic", """
def sum_to(n):
    return sum(range(n))

print(sum_to(4))
""", """
assert sum_to(4) == 10
""", """
def sum_to(n):
    return sum(range(n + 1))

print(sum_to(4))
""")

case("vowels_missing_u", "logic", """
def count_vowels(s):
    return sum(1 for c in s if c in "aeio")

print(count_vowels("education"))
""", """
assert count_vowels("education") == 5
""", """
def count_vowels(s):
    return sum(1 for c in s if c in "aeiou")

print(count_vowels("education"))
""")

case("mean_floor_division", "logic", """
def mean(xs):
    return sum(xs) // len(xs)

print(mean([1, 2]))
""", """
assert mean([1, 2]) == 1.5
""", """
def mean(xs):
    return sum(xs) / len(xs)

print(mean([1, 2]))
""")

case("binary_search_edges", "logic", """
def bsearch(xs, t):
    lo, hi = 0, len(xs) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if xs[mid] == t:
            return mid
        elif xs[mid] < t:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

print(bsearch([1, 3, 5], 3))
""", """
assert bsearch([1, 3, 5, 7], 7) == 3
assert bsearch([5], 5) == 0
assert bsearch([1, 2, 3], 4) == -1
""", """
def bsearch(xs, t):
    lo, hi = 0, len(xs) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if xs[mid] == t:
            return mid
        elif xs[mid] < t:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

print(bsearch([1, 3, 5], 3))
""")

case("dedupe_loses_order", "logic", """
def dedupe(xs):
    return list(set(xs))

print(dedupe([3, 1, 3, 2, 1]))
""", """
assert dedupe([3, 1, 3, 2, 1]) == [3, 1, 2]
""", """
def dedupe(xs):
    seen = set()
    out = []
    for x in xs:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

print(dedupe([3, 1, 3, 2, 1]))
""")

case("clamp_swapped", "logic", """
def clamp(x, lo, hi):
    return max(hi, min(x, lo))

print(clamp(5, 0, 10))
""", """
assert clamp(5, 0, 10) == 5
assert clamp(-1, 0, 10) == 0
assert clamp(11, 0, 10) == 10
""", """
def clamp(x, lo, hi):
    return max(lo, min(x, hi))

print(clamp(5, 0, 10))
""")

case("celsius_to_f", "logic", """
def c_to_f(c):
    return c * 9 / 5 - 32

print(c_to_f(100))
""", """
assert c_to_f(100) == 212
assert c_to_f(0) == 32
""", """
def c_to_f(c):
    return c * 9 / 5 + 32

print(c_to_f(100))
""")

case("factorial_loop_off", "logic", """
def fact(n):
    r = 1
    for i in range(1, n):
        r *= i
    return r

print(fact(5))
""", """
assert fact(5) == 120
assert fact(1) == 1
""", """
def fact(n):
    r = 1
    for i in range(1, n + 1):
        r *= i
    return r

print(fact(5))
""")

case("flatten_wrong_var", "logic", """
def flatten(xss):
    return [x for xs in xss for x in xss]

print(flatten([[1, 2], [3]]))
""", """
assert flatten([[1, 2], [3]]) == [1, 2, 3]
""", """
def flatten(xss):
    return [x for xs in xss for x in xs]

print(flatten([[1, 2], [3]]))
""")

case("word_count_spaces", "logic", """
def word_count(s):
    return len(s.split(" "))

print(word_count("hello world"))
""", """
assert word_count("hello   world foo") == 3
assert word_count("hello world") == 2
""", """
def word_count(s):
    return len(s.split())

print(word_count("hello world"))
""")

case("leap_year", "logic", """
def is_leap(y):
    return y % 4 == 0

print(is_leap(2024))
""", """
assert is_leap(2024)
assert not is_leap(1900)
assert is_leap(2000)
assert not is_leap(2023)
""", """
def is_leap(y):
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)

print(is_leap(2024))
""")

case("gcd_returns_zero", "logic", """
def gcd(a, b):
    while b:
        a, b = b, a % b
    return b

print(gcd(12, 18))
""", """
assert gcd(12, 18) == 6
assert gcd(7, 3) == 1
""", """
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

print(gcd(12, 18))
""")

case("chunk_drops_tail", "logic", """
def chunk(xs, n):
    return [xs[i:i + n] for i in range(0, len(xs) - n, n)]

print(chunk([1, 2, 3, 4, 5], 2))
""", """
assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
""", """
def chunk(xs, n):
    return [xs[i:i + n] for i in range(0, len(xs), n)]

print(chunk([1, 2, 3, 4, 5], 2))
""")

case("title_case_words", "logic", """
def title(s):
    return s.capitalize()

print(title("hello big world"))
""", """
assert title("hello big world") == "Hello Big World"
""", """
def title(s):
    return " ".join(w.capitalize() for w in s.split())

print(title("hello big world"))
""")

case("running_sum_lag", "logic", """
def running(xs):
    out = []
    t = 0
    for x in xs:
        out.append(t)
        t += x
    return out

print(running([1, 2, 3]))
""", """
assert running([1, 2, 3]) == [1, 3, 6]
""", """
def running(xs):
    out = []
    t = 0
    for x in xs:
        t += x
        out.append(t)
    return out

print(running([1, 2, 3]))
""")
