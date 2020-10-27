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


def test_two_qubit_grover():
    most_likely = Program("""
        // Note that we don't have qubit arrays yet!
        q1 <- split(?false);
        q2 <- split(?false);

        //// Target state is 11
        //// Note that this function closes over its enclosing environment.
        fn oracle() {
            if q1 {
                q2 <- phase(q2);
            }
        }

        fn diffuse() {
            q1 <- phase(split(q1));
            q2 <- ~q2;
            if q1 {
                q2 <- ~q2;
            }
            q1 <- split(q1);
        }

        for i in 0..1 {
            oracle();
            diffuse();
        }

        // Read out
        c1 <- !q1;
        c2 <- !q2;
    """).compile().sample(
        backends.CirqBackend(),
        reps=10
    ).most_likely()

    # The most likely measured value is c1=True, c2=True
    assert most_likely.c1 and most_likely.c2
