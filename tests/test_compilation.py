from pycavy import Program, backends

def test_bell_pair():
    results = Program("""
        q <- split(?false);
        r <- ?false;
        if q {
            r <- ~r;
        }

        // Read out the states of the now-entangled qubits.
        // Note that this behaviour is not supposed to be permanent.
        // It's a slight kludge.
        c <- !q;
        d <- !r;
        """).compile().sample(backends.CirqBackend(), reps=24)

    assert all([l == r for l, r in zip(results['c'], results['d'])])
